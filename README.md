# D2WordPress
Discord to WordPress image ingestion


A multithreaded Python script that uploads AI-generated images uploaded to Discord and sends the full high-resolution version of the image automatically to Amazon S3 storage (creates thumbnails as well) and also auto-creates each image as a post (along with the details) in the WordPress website. This is where either you as an author or people (if you share it with the online community) can see the image collection process in real-time (as the archiving process takes place). 

# Live Demo Website
For now, I've created the demo, to showcase how the script can be used to archive all images created by artificial intelligence, such as Midjourney, and sent to discord. So far it's capable of ingesting about 100 high-resolution images every 5 minutes. But can be adjusted for more. 

Currently hosted at: https://aiartgal.com 
