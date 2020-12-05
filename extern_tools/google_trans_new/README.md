# google_trans_new
### Version 1.1.9

A free and unlimited python API for google translate.  
It's very easy to use and solve the problem that the old api which use tk value cannot be used.  
This interface is for academic use only, please do not use it for commercial use.  
  
Version 1.1.9 have fixed url translate.
Ps:
If your get translations for different genders, it will return a list.
https://support.google.com/translate/answer/9179237?p=gendered_translations&hl=zh-Hans&visit_id=637425624803913067-1347870216&rd=1
***
  
  
Installation
====
```
pip install google_trans_new
```
***
  
  
Basic Usage
=====
### Translate
```python
from google_trans_new import google_translator  
  
translator = google_translator()  
translate_text = translator.translate('สวัสดีจีน',lang_tgt='en')  
print(translate_text)
-> Hello china
```
***

Advanced Usage
=====
### Translate 
```python  
from google_trans_new import google_translator  

# You can set the url_suffix according to your country. You can set url_suffix="hk" if you are in hong kong,url_suffix use in https://translate.google.{url_suffix}/ 
# If you want use proxy, you can set proxies like proxies={'http':'xxx.xxx.xxx.xxx:xxxx','https':'xxx.xxx.xxx.xxx:xxxx'}
translator = google_translator(url_suffix="hk",timeout=5,proxies={'http':'xxx.xxx.xxx.xxx:xxxx','https':'xxx.xxx.xxx.xxx:xxxx'})  
# <Translator url_suffix=cn timeout=5 proxies={'http':'xxx.xxx.xxx.xxx:xxxx','https':'xxx.xxx.xxx.xxx:xxxx'}>  
#  default parameter : url_suffix="cn" timeout=5 proxies={}
translate_text = translator.translate('สวัสดีจีน',lang_tgt='zh')  
# <Translate text=สวัสดีจีน lang_tgt=th lang_src=zh>  
#  default parameter : lang_src=auto lang_tgt=auto 
#  API can automatically identify the src translation language, so you don’t need to set lang_src
print(translate_text)
-> 你好中国
```
### Multithreading Translate
```python
from google_trans_new import google_translator 
from multiprocessing.dummy import Pool as ThreadPool
import time

pool = ThreadPool(8) # Threads

def request(text):
    lang = "zh"
    t = google_translator(timeout=5)
    translate_text = t.translate(text.strip(), lang)
    return translate_text

if __name__ == "__main__" :
    time1 = time.time()
    with open("./test.txt",'r') as f_p:
      texts = f_p.readlines()
      try:
          results = pool.map(request, texts)
      except Exception as e:
          raise e
      pool.close()
      pool.join()

      time2 = time.time()
      print("Translating %s sentences, a total of %s s"%(len(texts),time2 - time1))
-> Translating 720 sentences, a total of 25.89591908454895 s 
```
### Detect
```python
from google_trans_new import google_translator  
  
detector = google_translator()  
detect_result = detector.detect('สวัสดีจีน')
# <Detect text=สวัสดีจีน >  
print(detect_result)
-> ['th', 'thai']
```
### Pronounce
```python
from google_trans_new import google_translator  
  
translator  = google_translator()  
Pronounce = translator.transalate('สวัสดีจีน',lang_src='th',lang_tgt='zh',pronounce=True)  
print(Pronounce)
-> ['你好中国 ', 'S̄wạs̄dī cīn', 'Nǐ hǎo zhōngguó']
```
***

Prerequisites
====
* **Python >=3.6**  
* **requests**  
* **six**  
***
  
  
License
====
google_trans_new is licensed under the MIT License. The terms are as follows:  

```
MIT License  

Copyright (c) 2020 lushan88a  

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.  
```
