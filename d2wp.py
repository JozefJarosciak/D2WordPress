import datetime
from multiprocessing.pool import ThreadPool
from urllib.parse import urlparse
import boto3
import nltk
import re
import requests, json, os, base64
from io import BytesIO
import MySQLdb
import urllib3
from nltk.corpus import stopwords
from PIL import Image
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
st = time.time()
cachedStopWords = stopwords.words("english")
nltk.download('stopwords')
num = 0


def send_image_to_s3(url, name):
    bucket_name = 'yourwebsite.com'
    boto3.Session(profile_name='default')
    s3 = boto3.client('s3')
    response = requests.get(url)
    img = BytesIO(response.content)
    file_name = f'subfolder/{name}'
    r = s3.upload_fileobj(img, bucket_name, file_name, ExtraArgs={ "ContentType": "image/jpeg"})
    s3_path = 'https://s3.amazonaws.com/yourwebsite.com/subfolder/' + name
    return s3_path


def wp_upload_image(domain, user, password, imgPath):
    # imgPath can be local image path or can be url
    credentials = "{}:{}".format(user, password)
    token = base64.b64encode(credentials.encode())
    url = 'https://'+ domain + '/wp-json/wp/v2/media'
    filename = imgPath.split('/')[-1] if len(imgPath.split('/')[-1])>1 else imgPath.split('\\')[-1]
    extension = imgPath[imgPath.rfind('.')+1 : len(imgPath)]
    if imgPath.find('http') == -1:
        try: data = open(imgPath, 'rb').read()
        except Exception as ex:
            print(ex)
            return None
    else:
        rs = requests.get(imgPath)
        if rs.status_code == 200:
            data = rs.content
        else:
            print('url get request failed')
            return None


    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
        "Authorization": "Basic {}".format(token.decode("utf-8")),
        "content-type": "application/json",
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": str("image/" + extension)
    }

    rs = requests.post(url, headers=headers, data=data, verify=False)
    return (rs.json()['source_url'], rs.json()['id'])


def add_post(keywords,thumbnail,image,author,timestamp,image_orig,category,tags):
    # Init
    url = "https://yourwebsite.com/wp-json/wp/v2/posts"
    username = "AI"
    password = "wordpress password"
    credentials = "{}:{}".format(username, password)
    token = base64.b64encode(credentials.encode())

    # Header
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
        "Authorization": "Basic {}".format(token.decode("utf-8")),
        "content-type": "application/json",
    }
    keywords2 = keywords.replace(';', ',').replace('(', ',').replace(')', ',').replace('|', ',')
    keywords2 = keywords.split(',')
    # Post info
    post = {
        "title": keywords2[0].title(),
        "content": '<p></p><!-- wp:preformatted {"fontSize":"medium"} --><pre class="wp-block-preformatted has-medium-font-size"><strong>'+keywords+'</strong></pre><!-- /wp:preformatted --><!--more--><figure class="wp-block-image size-medium"><img class="alignnone" src="'+image+'" alt="'+keywords2[0].title()+'"/></figure><br>Archived Image: <a href="'+image_orig+'" target="_blank">URL</a><br>Author: <a href=/tag/'+author.replace(' ','-').replace(':','-').replace('.','-').lower()+'/>' + author + '</a>',

        "featured_media": thumbnail,
        "status": "publish",
        "categories":[str(category)],
        "tags":tags,
        "meta":[]
    }

    # Post
    r = requests.post(
        url,
        headers=headers,
        json=post,
        verify=False
    )


def retrieve_messages(channelid):
    global num
    # Create the connection object
    connection = MySQLdb.connect(
        host="mysql host",
        user="mysql user",
        port=3306,
        passwd="mysql password"
    )

    headers = {
        'authorization': 'discord headers authorization collected from the browser'
    }
    r = requests.get(
        f'https://discord.com/api/v10/channels/'+channelid+'/messages?limit=100',headers=headers 
    )
    jsonn = json.loads(r.text)
    cursor = connection.cursor()
    selected_category = 1
    if channelid == 'your selected channel for adding to specific wordpress categories':
        selected_category = 24
    else:
        selected_category = 1

    for value in jsonn:
        try:
            #if ('Upscaled by' in value['content'] or 'Upscaled (Beta) by' in value['content']) and '%' not in value['content']: #and '.png' in value['content']
            if ('Upscaled (Max)' in value['content']): #and '.png' in value['content']

                keywords_start2 = ''
                if '.png' in value['content'] or '.mj.' in value['content']:
                    keyword_start = (value['content'].split('**'))[1].split('**')[0]
                    keywords_start2 = keyword_start.rsplit('> ',1)
                    keywords_start2 = keywords_start2[1]
                else:
                    keyword_start = (value['content'].split('**'))[1].split('**')[0]
                    keywords_start2 = keyword_start.rsplit('> ',1)
                    keywords_start2 = keywords_start2[0]

                if '.mj.' in keywords_start2:
                    print(value['content'])
                    exit(0)

                #first upload thumbnail
                image_orig = value['attachments'][0]['url']
                keywords=keywords_start2.replace(' --upbeta', '').replace(' --uplight','')
                timestamp_orig = value['timestamp']

                sql_select_query = """ SELECT * FROM yourwebsite_urls.urls WHERE image_orig=%s"""
                cursor.execute(sql_select_query, (image_orig,))
                results = cursor.fetchall()
                row_count = cursor.rowcount
                if row_count == 0:
                    sql_select_query = """ SELECT * FROM yourwebsite_urls.urls WHERE keywords=%s and timestamp > (NOW() - INTERVAL 2 HOUR)"""
                    cursor.execute(sql_select_query, (keywords,))
                    row_count = cursor.rowcount
                    if row_count == 0:
                        keywords_split = ' '.join([word for word in keywords.split() if word not in cachedStopWords])
                        keywords_split = keywords_split.lower().replace(',',' ').replace(';',' ').replace('+', ' ').replace('(', ' ').replace(')', ' ').replace('_', ' ').replace('/', ' ')
                        keywords_split = re.sub(' +', ' ', keywords_split).split(" ")
                        keywords_split = list(filter(lambda i: len(i) > 1, keywords_split))
                        author = ''
                        if 'subfolder' in value['mentions'][0]['username'].lower():
                            author = value['mentions'][1]['username'].lower()
                        else:
                            author = value['mentions'][0]['username'].lower()

                        keywords_split.insert(0, author)
                        my_tag_id_list = []

                        for key in keywords_split:
                            sql_select_query = """ SELECT wp_terms.name,wp_terms.term_id FROM yourwebsite.wp_terms INNER JOIN yourwebsite.wp_term_taxonomy ON wp_terms.term_id = wp_term_taxonomy.term_id WHERE taxonomy='post_tag' AND wp_terms.name=%s;"""
                            cursor.execute(sql_select_query, (key,))
                            row_count = cursor.rowcount

                            if row_count == 0:
                                # insert tag that does not exist
                                sql_insert_query = """ INSERT INTO yourwebsite.wp_terms (name, slug) VALUES (%s,%s)"""
                                tuple1 = (key, key.replace(' ','-').replace(':','-').replace('.','-'))
                                cursor.execute(sql_insert_query, tuple1)
                                last_id = connection.insert_id()
                                connection.commit()

                                sql_insert_query = """ INSERT INTO yourwebsite.wp_term_taxonomy (term_taxonomy_id, term_id, taxonomy, description) VALUES (%s,%s,%s,%s);"""
                                tuple1 = (last_id, last_id,'post_tag', '')
                                cursor.execute(sql_insert_query, tuple1)
                                connection.commit()
                                my_tag_id_list.append(last_id)
                            else:
                                #exists, get an id for existing tag
                                pass
                                sql_select_query = """ SELECT wp_terms.term_id FROM yourwebsite.wp_terms WHERE name=%s;"""
                                cursor.execute(sql_select_query, (key,))
                                results = cursor.fetchone()
                                last_id = results[0]
                                my_tag_id_list.append(last_id)

                        image_file_name = urlparse(value['attachments'][0]['url'])
                        image_file_name = os.path.basename(image_file_name.path)

                        with open(image_file_name, 'wb') as f:
                            f.write(requests.get(image_orig).content)

                        imgg = Image.open(image_file_name)
                        imgg.thumbnail((250, 250))
                        imgg.save('th-' + image_file_name)
                        os.remove(image_file_name)

                        sql_insert_query = """ INSERT INTO yourwebsite_urls.urls (timestamp_orig, image_orig, keywords) VALUES (%s,%s,%s)"""
                        tuple1 = (timestamp_orig, image_orig, keywords)
                        cursor.execute(sql_insert_query, tuple1)
                        connection.commit()

                        thumbnail_upload_details = wp_upload_image('yourwebsite.com', 'AI', 'wordpress password here again', 'th-'+image_file_name)
                        size_thumb_new = os.path.getsize('th-'+image_file_name)
                        os.remove('th-'+image_file_name)

                        # upload full image to s3
                        image_upload_details = send_image_to_s3(url=value['attachments'][0]['url'],name=image_file_name)
                        size_image_orig = value['attachments'][0]['size']

                        #add post to wordpress with large image in s3
                        add_post(keywords=keywords,thumbnail=thumbnail_upload_details[1],image=image_upload_details,author=value['mentions'][1]['username'],timestamp=value['timestamp'],image_orig=value['attachments'][0]['url'], category=selected_category,tags=my_tag_id_list)
                        sql_update_query = """UPDATE yourwebsite_urls.urls set image_new=%s, thumbnail_new_id=%s, thumbnail_new=%s, size_image_orig=%s, size_thumb_new=%s, author=%s  WHERE image_orig=%s"""
                        tuple1 = (image_upload_details, thumbnail_upload_details[1], thumbnail_upload_details[0], int(size_image_orig), int(size_thumb_new),value['mentions'][1]['username'], image_orig)
                        cursor.execute(sql_update_query, tuple1)
                        connection.commit()
                        num=num+1
                        print('New Picture #', num, 'added:', keywords_start2)

                    else:
                        #print('Skipping',keyword_start[1])
                        pass
                else:
                    pass
                    #print('Already exists - Skipping')
        except Exception as ex:
           print(ex)
    cursor.close()
    connection.close()

channels_to_process = ['list of numeric wordpress channels separated by a comma']

channelcount=0

with ThreadPool(processes=20) as pool:
    #print('----*----- Processing Channel:',channelcount, 'of', len(channels_to_process), ':', channel)
    pool.map(retrieve_messages, channels_to_process)

print('--------------------------------------------------------------------------------------')
print('Total number of images from all channels', num)
print('--------------------------------------------------------------------------------------')


# get the end time
et = time.time()
# get the execution time
elapsed_time = et - st

print('Execution time:', str(datetime.timedelta(seconds=round(elapsed_time))))
