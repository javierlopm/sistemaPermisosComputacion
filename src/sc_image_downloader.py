from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from furl import furl
import re

# Valid students id formats
pattern    = []
pattern.insert(0 , re.compile("\d{7}"))
pattern.insert(1 , re.compile("\d{2}\-\d{5}"))
pattern.insert(2 , re.compile("\d{2}\-\d{5}\@usb\.ve"))

def format_id(student_id):
    if   re.match(pattern[0],student_id):
        return student_id
    elif (re.match(pattern[1],student_id) or re.match(pattern[2],student_id)):
        return student_id[0:2] + student_id[3:8]
    else:
        print ("Error: formato de carnet invalido para " + student_id +
               " probar con 0000000 , 00-00000 o 00-00000@usb.ve" )
        # raise Exception("studen_id format error" )
        return None

class CommunityServiceDownloader():

    def __init__(self,save_dir="SC_Imagenes/"):

        try:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            self.google_drive = GoogleDrive(gauth)
            self.save_dir = save_dir
        except Exception as e:
            print("Error autenticando para descargar las imágenes del SC")
            print(e)

    def download_image(self,image_drive_id,student_id):
        try:
            print(image_drive_id)
            print(student_id)
            print(self.save_dir)

            #student_id = format_id(str(student_id))
            save_path = "./" + self.save_dir + student_id
            image_file = self.google_drive.CreateFile({'id': image_drive_id})
            image_file.GetContentFile(save_path)

        except Exception as e:
            print("Error descargando la imagen con el ID " + image_drive_id)
            print(e)

    def get_googledrivefile_id(self,file_url):
        f = furl(file_url)
        return f.args['id']
