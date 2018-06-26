from selenium import webdriver

# driver = webdriver.PhantomJS() 更快
driver = webdriver.Chrome()
driver.get("http://search.kongfz.com/product_result/?status=0&catnum=17&pubdate=194901h201512&quality=70h&quaselect=3&price=5.00h2000.00&pagenum=10")
print (driver.current_url)
print (driver.title)
print (driver.page_source)
driver.close()