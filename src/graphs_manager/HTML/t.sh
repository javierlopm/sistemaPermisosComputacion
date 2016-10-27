requestInicial="$(curl --insecure -v https://secure.dst.usb.ve/login?service=https%3A%2F%2Fexpediente.dii.usb.ve%2Fexpediente%2Flogin.do 2>&1)"
lt="$(sed -n 's@.*<input type="hidden" name="lt" value="\([^"]*\)".*@\1@p' <<< "$requestInicial")"
SID="$(sed -n 's@.*< Set-Cookie: JSESSIONID=\([^;]*\);.*@\1@p' <<< "$requestInicial")"
username=$1
password=$2
#echo 'Insertar el username'
#read -r username
#echo 'Insertar el password'
#read -rs password
segundaLlamada="$(curl \
--insecure \
--data "username=$username&password=$password&lt=$lt&_eventId=submit&submit=INICIAR+SESI%C3%93N" \
  -v \
  -H "Cookie: JSESSIONID=${SID}" \
  -H 'Origin: https://secure.dst.usb.ve' \
  -H 'Referer: https://secure.dst.usb.ve/login?service=https%3A%2F%2Fexpediente.dii.usb.ve%2Fexpediente%2Flogin.do' \
"https://secure.dst.usb.ve/login?service=https%3A%2F%2Fexpediente.dii.usb.ve%2Fexpediente%2Flogin.do" 2>&1)"
url="$(grep Location: <<< "$segundaLlamada" | awk '{print $3 }')"
terceraLlamada="$(curl --insecure -v "$(grep Location: <<< "$segundaLlamada" | awk '{print $3 }')" 2>&1)"
SID2="$(sed -n 's@.*< Set-Cookie: JSESSIONID=\([^;]*\);.*@\1@p' <<< "$terceraLlamada")"
curl --insecure -i -s -v -H "Cookie: JSESSIONID=${SID2}" -H "Referer: $url" "https://expediente.dii.usb.ve/expediente/informeAcademico.do;jsessionid=${SID2}" >./HTML/$username.html



