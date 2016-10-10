target: cleanup

bd = build

buildform: 
	pyinstaller check_answers.py
	cp client_secret.json dist/check_answers
	cp -R /usr/local/selenium dist/check_answers
	tar -zcvf check_answers.tar.gz dist/check_answers

cleanup: buildform
	rm -rf build
	rm -rf dist
	rm -f *.spec

clean:
	rm -f coord_downloader.tar.gz check_answers.tar.gz
