from selenium import webdriver
from selenium.webdriver.common.by import By
import base64
import easyocr

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

        reader = easyocr.Reader(['en'])
        result = reader.readtext('captcha.jpg')

        for x in result:
         captchaResult = x[1]

        print(captchaResult)

        driver.find_element(By.XPATH, '//*[@id="code"]').send_keys(captchaResult)

        driver.find_element(By.XPATH, '//*[@id="captcha_test"]/p[2]/input[2]').click()
    except:
        print("Volviendo a intentar el captcha")
