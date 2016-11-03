target: buildform

# bd = buildf

buildform: 
	pyinstaller -F main_app.py
	cp client_secret.json dist
	cp -R Sql dist
	cp -R /usr/local/selenium dist
	cp  chromedriver dist
	cp -R graphs_manager dist
	mv dist main_app 
	tar -zcvf main_app.tar.gz main_app
	rm -rf build
	rm -rf dist
	rm -R main_app

clean:
	rm -f coord_downloader.tar.gz main_app.tar.gz
	rm -f *\.csv
	rm -rf build
	rm -rf dist
	rm -R main_app
