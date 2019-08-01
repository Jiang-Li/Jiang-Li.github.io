#!/bin/bash  

cp -r ../my-blog/public/* .

git add .  
git commit -m "generated on `date +'%Y-%m-%d %H:%M:%S'`";
git push origin master
