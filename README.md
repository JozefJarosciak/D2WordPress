# Discord Images to WordPress
Discord to WordPress image ingestion script.
Released as an open-source under the permissive MIT License.

# Description
A a multithreaded Python script that takes Discord images (e.g. Midjourney or any channel) and sends the full high-resolution version of the image automatically to Amazon S3 storage (creates thumbnails as well) and also auto-uploads each image as a new post (along with all the details) into the WordPress website. This is where either you (as an author) or people (if you share it with the online community) can see the image collection process in real-time (as the archiving process takes place).

Please don't comment on the quality of the code :). I had no time to clean it yet.

# Live Demo Website
For now, I've created the demo, to showcase how the script can be used to archive all images created by artificial intelligence, such as Midjourney, and sent to discord. So far it's capable of ingesting about 100 high-resolution images every 5 minutes with only 5 threads. But can be adjusted for thousands a minute as the script is fully multithreaded and you can run it with as many threads as your machine allows you to use and as you configure (through script variable).

Live demo currently hosted at: https://aiartgal.com

# Process Explained
![process diagram](https://preview.redd.it/xukb1e7jf2q91.jpg?width=2406&format=pjpg&auto=webp&s=4db173ff44cae791fb044ea448d9c2e6b50f796d)