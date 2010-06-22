(cd doc; make pdf; make pdf; make pdf)
tar cf ocd.tar doc/ocd.pdf
git clean -x -f
tar uf ocd.tar *.py graph2png.sh LICENSE README *.awk libdisassemble tests
gzip ocd.tar
