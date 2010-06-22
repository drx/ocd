(cd doc; make pdf; make pdf; make pdf)
tar cf /tmp/ocd.tar doc/ocd.pdf
git clean -x -f
tar uf /tmp/ocd.tar *.py graph2png.sh LICENSE README *.awk libdisassemble tests
cp /tmp/ocd.tar .
gzip ocd.tar
