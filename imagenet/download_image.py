import sys,os
import urllib
from urllib import urlopen
from urllib import urlretrieve
from urllib2 import URLError, HTTPError
import socket
import ssl
import argparse
import random
import io
from PIL import Image

def mkdir(path):
    if os.path.exists(path):
        return
    os.mkdir(path)

# arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data_dir',       type=str, default='images')
parser.add_argument('--num_of_classes', type=int, default=1000)
parser.add_argument('--num_of_pics',    type=int, default=10)

args = parser.parse_args()

urllib.FancyURLopener.prompt_user_passwd = lambda *a, **k: (None, None)
socket.setdefaulttimeout(30)

categories = {}
with open('words.txt', 'r') as f:
    for line in f:
        line = line.strip()
        word_id, label = line.split('\t')
        categories[word_id] = label.replace(' ', '_').replace(',', '_')

with open('imagenet.synset.obtain_synset_list', 'r') as f:
    word_ids = f.read().split()
random.shuffle(word_ids)

mkdir(args.data_dir)
for word_id in word_ids[:args.num_of_classes]:
    category = categories[word_id]
    count = 0
    if len(category) <= 0:
        print('empty category name for {}'.format(word_id))
        continue
    mkdir(os.path.join(args.data_dir, category))
    print(category)
    try:
        urls = urlopen('http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=' + word_id).read()
        urls = urls.split()
        random.shuffle(urls)

        for url in urls:
            print(url)
            filename = url.rsplit('/', 1)[1]
            try:
                output = os.path.join(args.data_dir, category, '{}_{}'.format(count, filename))
                urlretrieve(url, output)
                valid_image = False
                try:
                    # test: can open file as image or not
                    with open(output, 'rb') as f:
                        b = io.BytesIO(f.read())
                    image = Image.open(b)
                    size = os.path.getsize(output)
                    if size != 2051: #not flickr Error
                        valid_image = True
                except IOError:
                    pass
                if valid_image:
                    count += 1
                if not valid_image:
                    print 'not image file: {}'.format(filename)
                    os.remove(output)
            except HTTPError as e:
                print e.reason
            except URLError as e:
                print e.reason
            except ssl.CertificateError as e:
                print e
            except IOError as e:
                print e
            except:
                print 'unhandled error'
            if count >= args.num_of_pics:
                break
    except HTTPError, e:
        print e.reason
    except URLError, e:
        print e.reason
    except IOError, e:
        print e
    except:
        print 'unhandled error'
