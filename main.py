from selenium import webdriver
from selenium.webdriver.common.by import By
import base64
import easyocr
import cv2
import numpy as np

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

driver.get("https://www.galileo.edu/wp-content/plugins/si-captcha-for-wordpress/captcha/test/captcha_test.php")

captchaBool = False
while captchaBool is not True:
    try:
        captchaImage = driver.find_element(By.XPATH, '//*[@id="si_image"]')

        captchaImageSave = driver.execute_async_script("""
                    var ele = arguments[0], callback = arguments[1];
                    ele.addEventListener('load', function fn(){
                      ele.removeEventListener('load', fn, false);
                      var cnv = document.createElement('canvas');
                      cnv.width = this.width; cnv.height = this.height;
                      cnv.getContext('2d').drawImage(this, 0, 0);
                      callback(cnv.toDataURL('image/jpeg').substring(22));
                    }, false);
                    ele.dispatchEvent(new Event('load'));
                    """, captchaImage)

        with open(r"captcha.jpg", 'wb') as f:
         f.write(base64.b64decode(captchaImageSave))
        
        img = cv2.imread("captcha.jpg")
         
        # Convierte la imagen a escala de grises
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar un umbral para obtener solo los tonos de negro (y gris)
        _, imagen_umbral = cv2.threshold(
            gray_img, 150, 255, cv2.THRESH_BINARY_INV)

        # Crear una imagen en blanco
        imagen_blanca = np.ones_like(img) * 255

        # Aplicar la máscara de umbral a la imagen original
        resultado = cv2.bitwise_and(img, img, mask=imagen_umbral)

        # Combinar la imagen original con la imagen en blanco usando la máscara inversa
        imagen_final = cv2.add(imagen_blanca, resultado, mask=cv2.bitwise_not(imagen_umbral))

        # Aumentar el contraste en un 300%
        alpha = 4.0  # Factor de contraste (1.0 + 3.0 = 4.0 para +300%)
        imagen_contraste = cv2.convertScaleAbs(imagen_final, alpha=alpha, beta=0)

        # Aumentar el brillo en un 150%
        beta = 150  # Valor de brillo (150 para +150%)
        imagen_brillo = cv2.convertScaleAbs(imagen_contraste, alpha=1.0, beta=beta)
        
        cv2.imwrite("captcha.jpg", imagen_brillo)

        reader = easyocr.Reader(['en'])
        result = reader.readtext('captcha.jpg')

        for x in result:
         captchaResult = x[1]

        print(captchaResult)

        driver.find_element(By.XPATH, '//*[@id="code"]').send_keys(captchaResult)

        driver.find_element(By.XPATH, '//*[@id="captcha_test"]/p[2]/input[2]').click()
    except:
        print("Volviendo a intentar el captcha")
