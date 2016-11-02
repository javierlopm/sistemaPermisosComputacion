target: buildform

# bd = buildf

buildform: 
	pyinstaller -F main_app.spec
	cp client_secret.json dist
	cp -R Sql dist
	cp -R /usr/local/selenium dist
	cp -R graphs_manager dist
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
