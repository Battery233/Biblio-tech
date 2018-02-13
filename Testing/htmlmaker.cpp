#include "string.h"
#include "malloc.h"
#include <iostream>
#include <fstream.h>

using namespace std;

//this file is for the testing of the database list file
//not fully implemented yet

char *GetMidStr(const char*string,const char *left,const char *right)
{
    int string_len,left_len,right_len,i,flag=0,start,end,result_len;
    char *result;
    string_len = strlen(string);
    left_len = strlen(left);
    right_len = strlen(right);
    for(i=0;i<string_len;i++){
      if(*(string+i)==*left)
      {
        if(strnicmp(string+i,left,left_len)==0)
        {
          flag=1;
          start=i;
        }
      }

      if(flag==1 && *(string+i)==*right)
      {
        if(strnicmp(string+i,right,right_len)==0)
        {
            flag=2;
            end=i;
        }
      } 
      {
        result_len = end-start-left_len;
        flag=0;
        result = (char*)malloc(result_len+1);
        *(result+result_len)=0;
        strncpy(result,string+start+left_len,result_len);
      }
    }
    return result;
}

int main(void)
{
    string log = "";
    int leng=0,i;
    char *p="<a href=\"https://github.com/leo-mazz/sdp-group13/blob/master/Testing/databaselist.html">
             This file for the record of the database output </a>";
    char *left="<a href=\"https://github.com/leo-mazz/sdp-group13/blob/master/Testing/databaselist.html">";
    char *right="</a>";
    printf("%s",GetMidStr(p,left,right));
    
    log = GetMidStr(p,left,right);
    ofstream SaveFile(“databaselist.html”);
    SaveFile << log;
    SaveFile.close();

    return 0;
}
