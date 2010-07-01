/^[0-9a-f]* g.*text\t[0-9a-f]*[ ]*[a-z]*$/ {
    start[$NF]=$1;
    len[$NF]=$(NF-1);
}
END {
    for (i in start)
        print i, start[i], len[i];
}
