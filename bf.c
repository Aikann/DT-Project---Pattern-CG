#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int numRows;
int numFeatures;
int *rowClass;
int *rowClassPos;
int *nrFeatValues;
double **RowValues;
double **FeatValues;
// to be filled by initialisation procedure
int nrOfClasses;
int *classValues;
// classes in general, coded as integers

int cmpint(const void *p,const void *q) {
 int *pp,*qq;
 pp = (int *) p;
 qq = (int *) q;
 if      ( *pp-*qq  < 0 ) return (-1);
 else if ( *pp-*qq  > 0 ) return ( 1);
 else                     return ( 0 );
}

int cvPos(int cv) {
  int * pos= (int *) bsearch(&cv, classValues, nrOfClasses, sizeof(int),cmpint);
  if ( pos==NULL ) {
     printf("Error inside cvPos\n");
     return (0);
  } else {
     return ( pos-classValues );
  }
}

int cmpdbl(const void *p,const void *q) {
 double *pp,*qq;
 pp = (double *) p;
 qq = (double *) q;
 if      ( *pp-*qq  < 0 ) return (-1);
 else if ( *pp-*qq  > 0 ) return ( 1);
 else                     return ( 0 );
}

int thisF;
int cmpthreshold(const void *p,const void *q) {
 int *pp,*qq;
 pp = (int *) p;
 qq = (int *) q;
 double v1,v2;
 v1 = RowValues[*pp][thisF];
 v2 = RowValues[*qq][thisF];
 if      ( v1-v2  < 0 ) return (-1);
 else if ( v1-v2  > 0 ) return ( 1);
 else                   return ( 0 );
}


int readSampleFile(const char *fileName ) {
   FILE *fp=NULL;
   int nrComments=0, nrDataLines=0;
   int nrEntries=0;
   char linebuffer[1024];
   fp = fopen(fileName,"r");
   char *lb=NULL;
   lb = fgets(linebuffer,1024,fp);
   while ( lb!=NULL && linebuffer[0]=='#' ) {
      lb = fgets(linebuffer,1024,fp);
      nrComments++;
   }
   if ( lb!=NULL ) {
      const char s[2] = ",";
      char *token;
      /* get the first token */
      token = strtok(linebuffer, s);

      /* walk through other tokens */
      while( token != NULL ) {
         nrEntries++;
         //printf("%d:  %s\n", nrEntries, token );
         token = strtok(NULL, s);
      }
   }
   if ( nrEntries > 1 ) {
      const char s[2] = ",";
      char *token;
      nrDataLines++;
      lb = fgets(linebuffer,1024,fp);
      /* get the first token */
      token = strtok(linebuffer, s);
      while ( lb!=NULL && token!=NULL ) {
         nrDataLines++;
         lb = fgets(linebuffer,1024,fp);
         token = strtok(linebuffer, s);
      }
   }
   fclose( fp );
   // report
   printf("reading from file %s\n",fileName);
   printf("we find %d comment lines, followed by %d data lines\n",
          nrComments, nrDataLines );
   printf("the (first) data line contains %d entries - assumed numerical\n",
          nrEntries );

   numRows = nrDataLines; // initially set, there may be an empty line at the end
   numFeatures = nrEntries-1;
   int i,f,k,readint;
   double readdbl;
   rowClass = (int *) calloc(numRows,sizeof(int));
   rowClassPos = (int *) calloc(numRows,sizeof(int));
   nrFeatValues = (int *) calloc(numFeatures,sizeof(int));
   RowValues = (double **) calloc(numRows,sizeof(double *));
   FeatValues = (double **) calloc(numFeatures,sizeof(double *));
   for (i=0;i<numRows;i++) RowValues[i] = (double *) calloc(numFeatures,sizeof(double));
   for (i=0;i<numFeatures;i++) FeatValues[i] = (double *) calloc(numRows,sizeof(double));
   // too much space; clean out later
   // reopen file to fill arrays
   fp = fopen(fileName,"r");
   lb = NULL;
   lb = fgets(linebuffer,1024,fp);
   while ( lb!=NULL && linebuffer[0]=='#' ) {
      lb = fgets(linebuffer,1024,fp);
   }
   // we have now the first data line
   for (i=0;i<numRows;i++) {
     const char s[2] = ",";
     char *token;
     const char ch = ',';
     /* get the first token */
     if (lb==NULL) break;
     if ( strchr(linebuffer, ch )==NULL )  break;
     token = strtok(linebuffer, s);
     if (token==NULL) break;
     for (f=0;f< numFeatures ;f++) {
        sscanf(token,"%lf",&readdbl);
        RowValues[i][f]  = readdbl;
        FeatValues[f][i] = readdbl;
        if (i<=9) printf("%3g ,",readdbl);
        token = strtok(NULL, s);
     }
     sscanf(token,"%lf",&readdbl);
     readint = (int) readdbl;  // in case we read 0.0 or 1.0
     rowClass[i]=readint;
     if (i<=9) printf("%d \n",readint);
     lb = fgets(linebuffer,1024,fp);
  }
  if (i<numRows) numRows = i;
  for (f=0;f< numFeatures ;f++) {
     qsort(FeatValues[f],numRows,sizeof(double),cmpdbl);
     for (i=0,k=1; k<numRows; k++)
     if ( FeatValues[f][i]<FeatValues[f][k] ) {
          FeatValues[f][i+1]=FeatValues[f][k] ;
          i++;
     }
     nrFeatValues[f] = i;  // actually this means we skip last value
  }
  classValues = (int *) calloc(numRows,sizeof(int));
  for (i=0;i<numRows;i++) classValues[i] = rowClass[i];
  qsort(classValues,numRows,sizeof(int),cmpint);
  for (i=0,k=1; k<numRows; k++)
  if ( classValues[i]<classValues[k] ) {
       classValues[i+1]=classValues[k] ;
       i++;
  }
  nrOfClasses = i+1;

  for (i=0;i<numRows;i++) {
     rowClassPos[i]=  cvPos( rowClass[i] ) ;
  }
  printf("problem statistics \n");
  printf("num Rows = %d, num Features = %d\n",numRows, numFeatures);
  printf("num RowClasses = %d\nClasses: ",nrOfClasses);
  printf(" %d", classValues[0]);
  for (i=1;i<nrOfClasses;i++) printf(", %d", classValues[i]);
  printf("\n");
  printf("num of thresholds per feature (one less than distinct values)\n");
  for (f=0;f<numFeatures;f++) {
     printf("feat_%d: %3d ; range: %3g - %3g\n",
     f, nrFeatValues[f], FeatValues[f][0], FeatValues[f][nrFeatValues[f]] );
  }
}

int readDiabetes() {
  int nl=768;
  int i,f,k,readint;
  double readdbl;
  numRows = nl;
  numFeatures = 8;
  rowClass = (int *) calloc(numRows,sizeof(int));
  rowClassPos = (int *) calloc(numRows,sizeof(int));
  nrFeatValues = (int *) calloc(numFeatures,sizeof(int));
  RowValues = (double **) calloc(numRows,sizeof(double *));
  FeatValues = (double **) calloc(numFeatures,sizeof(double *));
  for (i=0;i<numRows;i++) RowValues[i] = (double *) calloc(numFeatures,sizeof(double));
  for (i=0;i<numFeatures;i++) FeatValues[i] = (double *) calloc(numRows,sizeof(double));
  // too much space; clean out later
  FILE *fp=NULL;
  fp=fopen("diabetes.csv","r");
  for (i=0;i<nl;i++) {
     for (f=0;f<8;f++) {
        fscanf(fp,"%lf",&readdbl);
        fscanf(fp,",");
        RowValues[i][f]  = readdbl;
        FeatValues[f][i] = readdbl;
        if (i<=9) printf("%3g ,",readdbl);
     }
     fscanf(fp,"%lf",&readdbl);
     readint = (int) readdbl;  // in case we read 0.0 or 1.0
     rowClass[i]=readint;
     if (i<=9) printf("%d \n",readint);
  }
  for (f=0;f<8;f++) {
     qsort(FeatValues[f],numRows,sizeof(double),cmpdbl);
     for (i=0,k=1; k<numRows; k++)
     if ( FeatValues[f][i]<FeatValues[f][k] ) {
          FeatValues[f][i+1]=FeatValues[f][k] ;
          i++;
     }
     nrFeatValues[f] = i;  // actually this means we skip last value
  }
  nrOfClasses = 2;
  classValues = (int *) calloc(2,sizeof(int));
  classValues[0] = 0; classValues[1] = 1;
  for (i=0;i<nl;i++) rowClassPos[i]=rowClass[i];
  printf("problem statistics Indians Diabetes\n");
  printf("num Rows = %d, num Features = %d\n",numRows, numFeatures);
  printf("num of thresholds per feature (one less than distinct values)\n");
  for (f=0;f<numFeatures;f++) {
     printf("feat_%d: %3d ; range: %3g - %3g\n",
     f, nrFeatValues[f], FeatValues[f][0], FeatValues[f][nrFeatValues[f]] );
  }
}

int prt(int i) {
  return ( (i-1)/2 );
}
int lft(int i) {
  return ( (i<=1 ? 1 : (i==2 ? 0 : lft(prt(i)) ) ) );
}
int tdep(int i) {
  return ( (i<=0 ? 0 : 1+tdep(prt(i)) ) );
}



int bf2(int dep, int *cntSc, int lenR, int *Rid, int *Fid, int *ValId, int *prof, int *pred, int *card) {
   if ( dep==1 ) {
      // first check perfect set
      int r,nrRT=0;
      for (r=0;r<lenR;r++) {
         if ( rowClassPos[Rid[r]]==rowClassPos[Rid[0]] ) nrRT++;
      }
      // if all are the same, guess the obvious
      if ( nrRT==lenR ) {
        int predAll = rowClassPos[Rid[0]];
        // branch on feat_0 threshold 0
        int nrlft=0;
        int i,j,k;
        for (i=0;i<lenR;i++) {
           if ( RowValues[Rid[i]][0]<=FeatValues[0][0] ) nrlft++;
        }
        Fid[0] = 0;
        ValId[0]=0;
        prof[0] = lenR;
        card[0] = lenR;
        for (i=1;i<=2;i++) {
           Fid[i] = 0; ValId[i] = 0; pred[i] = predAll; prof[i] = 0; card[i] = 0;
        }
        for (j=1; j<=dep; j++) {
           i = (01<<j)   - 1; prof[i] = card[i] = nrlft;
           i = 2*(01<<j) - 2; prof[i] = card[i] = lenR-nrlft;
        }
        return ( lenR );
      }
      // passing this point we have distinct scores in our set of rows
      // in particular lenR >= 2
      int res,maxres=0;
      int f,v,i,j,k;
      int *RidNew = (int *) calloc(lenR,sizeof(int));
      int *RidCum = (int *) calloc(lenR,sizeof(int));
      int *lmax   = (int *) calloc(lenR,sizeof(int));
      int *rmax   = (int *) calloc(lenR,sizeof(int));
      int *lmaxId = (int *) calloc(lenR,sizeof(int));
      int *rmaxId = (int *) calloc(lenR,sizeof(int));
      int *ClsCnt = (int *) calloc(nrOfClasses,sizeof(int));
      for (i=0;i<lenR;i++) RidNew[i]=Rid[i];
      for ( f=0; f<numFeatures; f++ )  {
        thisF = f;
        qsort(RidNew,lenR,sizeof(int),cmpthreshold);
        for (i=0;i<nrOfClasses;i++) ClsCnt[i]=0;
        for (i=0;i<lenR;i++) {
           k = rowClassPos[RidNew[i]];
           RidCum[i] = 1 + (ClsCnt[ k ]++);
           if (i==0) {
              lmax[i]   = 1;
              lmaxId[i] = k;
           }
           else {
              if (RidCum[i] > lmax[i-1]) {
                 lmax[i]   = RidCum[i];
                 lmaxId[i] = k;
              }
              else {
                 lmax[i]   = lmax[i-1];
                 lmaxId[i] = lmaxId[i-1];
              }
           }
        }
        // next we store frequencies from right to left
        rmax[lenR-1]   = 1;
        rmaxId[lenR-1] = rowClassPos[RidNew[lenR-1]];
        for (i=lenR-2;i>=0;i--) {
           k = rowClassPos[RidNew[i]];
           if ( cntSc[k]+1-RidCum[i] > rmax[i+1]) {
              rmax[i]   = cntSc[k]+1-RidCum[i];
              rmaxId[i] = k;
           }
           else {
              rmax[i]   = rmax[i+1];
              rmaxId[i] = rmaxId[i+1];
           }
        }
        // now we can pick the best split
        for (i=1;i<lenR;i++) {
           if (RowValues[RidNew[i-1]][f]<RowValues[RidNew[i]][f]) {
              res = lmax[i-1] + rmax[i];
              if (maxres < res) {
                 maxres   = res;
                 Fid[0]   = f;
                 double th=RowValues[RidNew[i-1]][f];
                 double * vpos= (double *)bsearch(&th, FeatValues[f],
                                 nrFeatValues[f]+1,sizeof(double),cmpdbl);
                 v = vpos-FeatValues[f];
                 // just double check
                 if (th!=FeatValues[f][v]) {
                    printf("Reporting wrong position!\n");
                 }
                 ValId[0] = v;
                 prof[0]  = res;
                 card[0]  = lenR;
                 prof[1]  = lmax[i-1];   prof[2] = rmax[i];
                 pred[1]  = lmaxId[i-1]; pred[2] = rmaxId[i];
                 card[1]  = i;           card[2] = lenR-(i);
              }
           }
        }
      }
      free ( RidNew ); free ( RidCum ); free ( ClsCnt );
      free ( lmax ); free ( rmax );
      free ( lmaxId ); free ( rmaxId );
      return ( maxres );
   }
   else {
      int len,orglen;
      len = 2*(01<<(dep-1))-1;
      orglen = 2*(01<<(dep))-1;
      int r,nrRT=0;
      for (r=0;r<lenR;r++) {
         if ( rowClassPos[Rid[r]]==rowClassPos[Rid[0]] ) nrRT++;
      }
      // if all are the same, guess the obvious
      if ( nrRT==lenR ) {
        int predAll = rowClassPos[Rid[0]];
        // branch on feat_0 threshold 0
        int nrlft=0;
        int i,j,k;
        for (i=0;i<lenR;i++) {
           if ( RowValues[Rid[i]][0]<=FeatValues[0][0] ) nrlft++;
        }
        Fid[0] = 0;
        ValId[0]=0;
        prof[0] = lenR;
        card[0] = lenR;
        for (i=1;i<orglen;i++) {
           Fid[i] = 0; ValId[i] = 0; pred[i] = predAll; prof[i] = 0; card[i] = 0;
        }
        for (j=1; j<=dep; j++) {
           i = (01<<j)   - 1; prof[i] = card[i] = nrlft;
           i = 2*(01<<j) - 2; prof[i] = card[i] = lenR-nrlft;
        }
        return ( lenR );
      }
      else {
        int* Rid1 = (int *) calloc(lenR,sizeof(int));
        int* Fid1 = (int *) calloc(len,sizeof(int));
        int* Vid1 = (int *) calloc(len,sizeof(int));
        int* prof1 = (int *) calloc(len,sizeof(int));
        int* pred1 = (int *) calloc(len,sizeof(int));
        int* card1 = (int *) calloc(len,sizeof(int));
        int* Rid2 = (int *) calloc(lenR,sizeof(int));
        int* Fid2 = (int *) calloc(len,sizeof(int));
        int* Vid2 = (int *) calloc(len,sizeof(int));
        int* prof2 = (int *) calloc(len,sizeof(int));
        int* pred2 = (int *) calloc(len,sizeof(int));
        int* card2 = (int *) calloc(len,sizeof(int));
        int *ClsCnt1 = (int *) calloc(nrOfClasses,sizeof(int));
        int *ClsCnt2 = (int *) calloc(nrOfClasses,sizeof(int));
        // create for each candidate rootnode two subproblems
        // overwrite solution if improvement;
        int res,res1,res2,p1,p2,maxres=0;
        int f,v,r,i,j,k;
        int splitfound=0;
        for ( f=0; f<numFeatures; f++ ) {
          if ( nrFeatValues[f]>0 ) {
            // exclude features with fixed outcome
            int maxres2F=lenR; // upper bound on score in second tree
            double *thr = (double *) calloc(lenR,sizeof(double));
            for (r=0;r<lenR;r++) thr[r]= RowValues[Rid[r]][f];
            qsort(thr,lenR,sizeof(double),cmpdbl);
            for (i=0,k=1;k<lenR;k++) {
              if ( thr[i]<thr[k] ) {
                 thr[i+1]=thr[k]; i++;
              }
            }
            int thrL=i+1; // real number of distinct f values found
            if (thrL==1) {
               continue;  // with next f
            }
            else {
               splitfound = 1;
            }
            for ( v=0; v<nrFeatValues[f]; v++ ) {
              if ( bsearch( FeatValues[f]+v,
                            thr,thrL,sizeof(double),cmpdbl)!=NULL ) {
                // only thresholds attained by some r in Rid matter
                int len1=0,len2=0;
                for (i=0;i<nrOfClasses;i++) {
                   ClsCnt1[i] = ClsCnt2[i] = 0;
                }
                for ( r=0; r<lenR; r++ ) {
                  if ( RowValues[Rid[r]][f] <= FeatValues[f][v] ) {
                    Rid1[len1++] = Rid[r];
                    k = rowClassPos[Rid[r]];
                    ClsCnt1[k]++;
                  }
                  else {
                    Rid2[len2++] = Rid[r];
                    k = rowClassPos[Rid[r]];
                    ClsCnt2[k]++;
                  }
                }
                res1 = bf2(dep-1, ClsCnt1, len1, Rid1,
                           Fid1, Vid1, prof1, pred1, card1) ;
                if ( (res1 + len2 > maxres) && (res1 + maxres2F > maxres) ) {
                  res2 = bf2(dep-1, ClsCnt2, len2, Rid2,
                             Fid2, Vid2, prof2, pred2, card2) ;
                  maxres2F = res2;
                }
                else {
                    res2 = 0; // no need to explore second tree
                }
                res  = res1+res2;
                if (maxres < res) {
                  maxres   = res;
                  Fid[0]   = f;
                  ValId[0] = v;
                  prof[0]  = res;
                  card[0]  = lenR;
                  // remainder is union of the two solutions
                  for ( i=1; i<orglen; i++) {
                     int lf,nr;
                     lf = lft(i);
                     nr = ( lf ? i - ( 01<<(tdep(i)-1) ) : i - ( 01<<(tdep(i) ) ) );
                     if ( lf ) {
                        Fid[i]   = Fid1[nr];
                        ValId[i] = Vid1[nr];
                        prof[i]  = prof1[nr];
                        pred[i]  = pred1[nr];
                        card[i]  = card1[nr];
                     }
                     else {
                        Fid[i]   = Fid2[nr];
                        ValId[i] = Vid2[nr];
                        prof[i]  = prof2[nr];
                        pred[i]  = pred2[nr];
                        card[i]  = card2[nr];
                     }
                  }
                }
              }
            }
            free ( thr );
          }
        }
        if (splitfound==0) {
           // set of rows is indistinguishable by features, but
           // they may have different scores
           int pmax=-1;
           for (i=0;i<nrOfClasses;i++) if ( pmax<0 || maxres < cntSc[i] ) {
              pmax = i; maxres = cntSc[i];
           }
           // branch on feat_0 threshold 0
           // they all go left or all go right
           int nrlft=0;
           int i,j,k;
           for (i=0;i<lenR;i++) {
              if ( RowValues[Rid[i]][0]<=FeatValues[0][0] ) nrlft++;
           }
           Fid[0] = 0;
           ValId[0]=0;
           prof[0] = maxres;
           card[0] = lenR;
           for (i=1;i<orglen;i++) {
              Fid[i] = 0; ValId[i] = 0; pred[i] = pmax; prof[i] = 0; card[i] = 0;
           }
           for (j=1; j<=dep; j++) {
              i = (01<<j)   - 1; prof[i] =  (nrlft>0 ? maxres : 0 ); card[i] = nrlft;
              i = 2*(01<<j) - 2; prof[i] =  (nrlft==0? maxres : 0 ); card[i] = lenR-nrlft;
           }
        }

        // cleanup arrays of subtrees
        free ( Rid1 ); free ( Fid1 ); free ( Vid1 );
        free (prof1 ); free ( pred1 ); free ( card1 );
        free ( Rid2 ); free ( Fid2 ); free ( Vid2 );
        free (prof2 ); free ( pred2 ); free ( card2 );
        free ( ClsCnt1 ); free ( ClsCnt2 );
        return ( maxres );
      }
   }
}

int bf1(int dep, int nrR, int *Rid, int *Fid, int *ValId, int *prof, int *pred, int *card) {
   if ( dep<0 || nrR < 0 || prof==NULL || pred==NULL || card==NULL ) { return ( -1 ); }
   if ( nrR <= 1 ) return ( nrR );
   int *cntSc = NULL;
   cntSc = (int*) calloc(nrOfClasses,sizeof(int));
   int i,rw,res;
   for ( i=0; i<nrOfClasses; i++ )  cntSc[i]=0;
   for ( i=0; i<nrR; i++ )  {
     rw = rowClassPos[Rid[i]];
     cntSc[ rw ]++;
   }
   if ( dep==0 ) {
      int pmax=-1;
      for ( i=0; i<nrOfClasses; i++ )  if ( pmax<0 || res < cntSc[i] ) {
         pmax = i; res = cntSc[i];
      }
      prof[0] = res;
      pred[0] = pmax;
      card[0] = nrR;
      free ( cntSc );
      return ( res );
   }
   else {
      res = bf2(dep, cntSc, nrR, Rid, Fid, ValId, prof, pred, card);
      if ( cntSc!=NULL ) free ( cntSc );
      return ( res );
   }
}

int main() {

FILE *f = fopen("file.txt", "w");

 if (f == NULL)
 {
     printf("Error opening file!\n");
     exit(1);
 }
 // initialise data form csv file
 //
 // build arrays
 int TreeDep = 2;
 int len,lenR,i,j,k;
 len = 2*(01<<(TreeDep))-1;

 readSampleFile("myfile");


 //readDiabetes();

 // read input from file -
 lenR = numRows;

 if(lenR!=0){

 int* Rid = (int *) calloc(lenR,sizeof(int));
 int* Fid = (int *) calloc(len,sizeof(int));
 int* ValId = (int *) calloc(len,sizeof(int));
 int* prof = (int *) calloc(len,sizeof(int));
 int* pred = (int *) calloc(len,sizeof(int));
 int* card = (int *) calloc(len,sizeof(int));
 for (i=0;i<lenR;i++) Rid[i]=i;
 int res = bf1(TreeDep, lenR, Rid, Fid, ValId, prof, pred, card) ;

 printf("\nmax score for dep=%d is %d/%d\n",TreeDep,res,lenR);
 if ( res > 1 ) {
    printf("selecting root feature %d <= %3g \n",
            Fid[0], FeatValues[Fid[0]][ValId[0]]);
    for (k=0;k<len/2;k++)
      printf("Nd%d : res %d/%d, Feat_%d, threshold %g\n",
             k, prof[k], card[k], Fid[k], FeatValues[Fid[k]][ValId[k]]);
    for ( ; k<len ; k++)
      printf("Nd%d : res %d/%d, pred %d\n",
             k,prof[k],card[k],classValues[pred[k]]);
 } else {
    printf("unexpected outcome\n");
 }

 fprintf(f, "%d\n",res);
 fprintf(f,"selecting root feature %d <= %3g \n",Fid[0], FeatValues[Fid[0]][ValId[0]]);
  for (k=0;k<len/2;k++) fprintf(f,"Nd%d : res %d/%d, Feat_%d, threshold %Lf\n",
                               k, prof[k], card[k], Fid[k], FeatValues[Fid[k]][ValId[k]]);
  for ( ; k<len ; k++) fprintf(f,"Nd%d : res %d/%d, pred %d\n",k,prof[k],card[k],pred[k]);
 }

 else{

 fprintf(f, "0\n");
 fprintf(f,"selecting root feature 0 <= 0 \n");
  for (k=0;k<len/2;k++) fprintf(f,"Nd%d : res 0/0, Feat_0, threshold 0\n");
  for ( ; k<len ; k++) fprintf(f,"Nd%d : res 0/0, pred 0\n");
 }
 fclose(f);

}
