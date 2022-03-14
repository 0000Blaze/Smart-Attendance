import wget


def imageDownloader(fixed_url,varying_url):
    try:
        url = fixed_url + varying_url + ".png"
        file_name = wget.download(url)
    except:
        try:
            url = fixed_url + varying_url + ".jpg"
            file_name = wget.download(url)
        except:
            url = fixed_url + varying_url + ".jpeg"
            file_name = wget.download(url)
    print('Image Successfully Downloaded: ', file_name)

#fixed url part for all PUL075BCT students
fixed_url = "https://exam.ioe.edu.np/Images/StudentCurrentImage/3036/PUL075BCT"

#Total number of students in batch
i=96        
while i>0:
    if i<10:
        varying_url = "00" + str(i)
    elif i == 87 or i == 73  or i == 36 or i == 17:   #dropouts 87 73 36 17
        i= i-1
        continue
    else:
        varying_url = "0" + str(i)

    imageDownloader(fixed_url,varying_url)
    i = i-1

#download images of new added students
varying_url = "100"
imageDownloader(fixed_url,varying_url)
x= int(varying_url) - 1
while x > 96:    
    varying_url = "0" + str(x)
    imageDownloader(fixed_url,varying_url)
    x = x-1