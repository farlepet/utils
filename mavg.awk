#!/usr/bin/awk -f

# USAGE: ... | mavg.awk -vn=<n_avg>

BEGIN {
    m=int((n+1)/2)
}

{
    for(i = 2; i <= NF; i++) {
        L[i-1][NR]=$i; sum[i-1]+=$i;
    }
}

NR>=m {
    di++;
    d[di]=$1;
}

NR>n {
    for(i = 1; i < NF; i++) {
        sum[i]-=L[i][NR-n];
    }
}

NR>=n{
    k++;
    for(i = 1; i < NF; i++) {
        a[i][k]=sum[i]/n;
    }
}

END {
    for (j=1; j <= k; j++) {
        #printf "%f%s",d[j],OFS
        printf "%d%s",d[j],OFS
        for(i = 1; i < NF; i++) {
            printf "%f%s",a[i][j],OFS
        }
        print ""
    }
}

