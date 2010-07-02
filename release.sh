(cd doc; make pdf; make pdf; make pdf)
tar cf /tmp/ocd.tar doc/ocd.pdf
git clean -x -f
tar uf /tmp/ocd.tar graph2png.sh LICENSE README.textile ocd src tests
cp /tmp/ocd.tar .
gzip ocd.tar
