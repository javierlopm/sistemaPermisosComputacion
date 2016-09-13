target: cleanup

bd = build

buildform: 
	pyinstaller check_answers.py
	cp client_secret.json dist/check_answers
	tar -zcvf check_answers.tar.gz dist/check_answers


builddownloader:
	pyinstaller coord_downloader.py
	cp -R /usr/local/selenium dist/coord_downloader
	cp carnets.txt dist/coord_downloader
	tar -zcvf coord_downloader.tar.gz dist/coord_downloader

cleanup: buildform builddownloader
	rm -rf build
	rm -rf dist
	rm -f *.spec

clean:
	rm -f coord_downloader.tar.gz check_answers.tar.gz
