FILE=`date +%Y%m%d/%H00/%Y%m%d%H%M%S.jpg`
DIR=`dirname ${FILE}`
BASEDIR=`dirname ${DIR}`
echo "${FILE} ${DIR} ${BASEDIR}"
#mkdir -p $DIR
#raspistill -o ${FILE}
echo "mkcol ${BASEDIR}" > cmd.txt
echo "mkcol ${DIR}" >> cmd.txt
echo "put cmd.txt ${FILE}" >> cmd.txt
cadaver https://jfclere.myddns.me/webdav/ < cmd.txt
