
import requests
import re
import os
import sys 
from multiprocessing.pool import ThreadPool

#CONFIG
thumbnails_regex_list = [
    "-\d{1,4}x\d{1,4}$", #match: -421x421
    "-e\d{13}$", #match: -e1676678024195
    "-scaled$", 
    "-modified", 
]
#END CONFIG

if os.path.exists(os.path.abspath(sys.argv[0])):
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

if len(sys.argv) < 2:
    print("usage: manin.py [site]")
    print("e.g. python3 main.py wp-site.com")
    exit()
    
site = sys.argv[1]
if site.split("/") not in ["http", "https"]:
    site = "http://"+ site
site = os.path.join(site,'wp-content','uploads/')
content_list = []



def get_content_urls():
    global content_list
    print("\nSearching content to download...", flush=True)

    dates = []
    
    #Get directories by year
    response = requests.get(site)
    years = re.findall('alt="\[DIR\]"> <a href="(\d{2,4})\/"', str(response.content.decode()))
    
    #Set directories to examinate
    for year in years:
        response = requests.get(site+"/"+year)
        #Get directories by month
        months=re.findall('alt="\[DIR\]"> <a href="(\d{2})\/"', str(response.content.decode()))
        for month in months:
            dates.append(year+'/'+month)
    
 
    #Get all urls to download
    for date in dates:
        print("Listing "+site+date, flush=True, end="")

        #Get files ordered by size desc
        response = requests.get(site+date+"?C=S;O=D")
        temp_files=[]
        for file in re.findall('alt="\[(?!PARENTDIR).*\]"> <a href="(.+)"', str(response.content.decode())):
            temp_files.append(os.path.join(site,date,file))
            
        print(" - "+str(len(temp_files))+"  files found")

        content_list+=temp_files

        f = open(os.getcwd()+"/last_fetched_urls.txt", "w")
        f.write(str(content_list).replace(",",",\n"))
        f.close()

    print(' ===Total: '+str(len(content_list))+' files found===\n')
    #Create Directories
    create_dirs(dates)
    

    
#Create Directories
def create_dirs(dates=[]):
    for date in dates:
        dirname = os.path.join(os.getcwd(),site.replace("https://","").replace("http://","")+date)
        
        if not os.path.exists(dirname):
            print("New path created: "+dirname.replace(os.getcwd()+"/",""))
            os.makedirs(dirname)

def remove_already_downloaded():
    global content_list
    print("Skipping already downloaded files...", flush=True,)

    new_urls_list =[]

    for url in content_list:
        file_path=url.replace("https://","").replace("http://","")
        if not os.path.exists(os.path.join(os.getcwd(),file_path)):
            new_urls_list.append(url)
    
    print("Files skipped: "+ str(len(content_list)-len(new_urls_list)))
    print("==="+ str(len(new_urls_list))+" files to download===")
    content_list = new_urls_list[:]


def remove_thumbnails():
    if len(thumbnails_regex_list) == 0:
        return
    global content_list
    print("Skipping thumbnails...", flush=True,)
    thumbnails_count = 0
    for regex in thumbnails_regex_list:
        for image in content_list[:]:
            sub_res=re.search(regex,image.split(".")[-2])

            #If it is a thumbnail, search for the original file
            if sub_res is not None:
                if image.replace(sub_res[0],"") in content_list:
                    #Remove only if htere is a original file
                    content_list.remove(image)
                    thumbnails_count += 1
                    remove_local_file(image)

    print("Thumbnails found: "+ str(thumbnails_count)) 
    print("==="+str(len(content_list))+ " files remaining===\n")
 

def remove_local_file(remote_url):
    file_path=os.path.join(os.getcwd(),remote_url.replace("https://","").replace("http://",""))
    if os.path.exists(file_path):
        os.remove(file_path)

#Download video
def download(url):
    response = requests.get(url, stream=True)
    file_path=os.path.join(os.getcwd(),url.replace("https://","").replace("http://",""))
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for data in response:
                file.write(data)

        return url+" - Success"
    else:
        return url+" - error server returned "+ str(response.status_code)
    

def start():
    # Run 10 multiple threads. Each call will take the next element in urls list
    results = ThreadPool(10).imap_unordered(download, content_list)
    for r in results:
        print(r)


get_content_urls()
remove_thumbnails()
remove_already_downloaded()
if len(content_list) > 0:
    print("\nDownloading...", )
start()