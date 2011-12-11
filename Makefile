PUB=static/
CSS=${PUB}css/giflord.css
JS=${PUB}js/libs/jquery.tools.min.js ${PUB}js/libs/jquery.history.js ${PUB}js/libs/jquery.masonry.min.js ${PUB}js/libs/jquery.imagesloaded.js ${PUB}js/libs/jquery.infinitescroll.min.js ${PUB}js/giflord.js
BUILD=/tmp/
COMPRESSOR=/usr/local/Cellar/yuicompressor/2.4.7/bin/yuicompressor
VPATH=${BUILD}

all: giflord.min.css giflord.min.js install

giflord.min.css: ${CSS}
	${COMPRESSOR} --type css $< -o ${BUILD}$@

giflord.min.js: combined.js
	${COMPRESSOR} --type js ${BUILD}$< -o ${BUILD}$@

combined.js: ${JS}
	cat $^ > ${BUILD}$@

install: giflord.min.css giflord.min.js
	cp ${BUILD}giflord.min.css ${PUB}css/ && cp ${BUILD}giflord.min.js ${PUB}js/

clean:
	rm ${BUILD}giflord.min.css ${BUILD}giflord.min.js ${BUILD}combined.js

.PHONY: install clean
