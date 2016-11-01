# target: cleanup

bd = build

buildform: 
	pyinstaller -F main_app.py
	cp client_secret.json dist
	cp -R Sql dist
	cp -R /usr/local/selenium dist
	# tar -zcvf main_app.tar.gz dist/main_app

cleanup: buildform
	rm -rf build
	rm -rf dist
	rm -f *.spec

clean:
	rm -f coord_downloader.tar.gz main_app.tar.gz
	rm -f *\.csv
	rm -rf build
	rm -rf dist
	rm -f *.spec
