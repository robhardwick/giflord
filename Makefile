CSS=static/css/giflord.css
JS=static/js/libs/jquery.tools.min.js static/js/libs/jquery.masonry.min.js static/js/libs/jquery.imagesloaded.js static/js/libs/jquery.infinitescroll.min.js static/js/giflord.js
PUB=static/
BUILD=/tmp/
COMPRESSOR=/usr/local/Cellar/yuicompressor/2.4.7/bin/yuicompressor
VPATH=${BUILD}

all: giflord.min.css giflord.min.js install

giflord.min.css: ${CSS}
	${COMPRESSOR} --type css $< -o ${BUILD}$@

giflord.min.js: combined.js
	${COMPRESSOR} --type js $< -o ${BUILD}$@

combined.js: ${JS}
	cat $^ > ${BUILD}$@

install: giflord.min.css giflord.min.js
	cp ${BUILD}giflord.min.css ${PUB}css/ && cp ${BUILD}giflord.min.js ${PUB}js/

clean:
	rm ${BUILD}giflord.min.css ${BUILD}giflord.min.js

.PHONY: install clean
