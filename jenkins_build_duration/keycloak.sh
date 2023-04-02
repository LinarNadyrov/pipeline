#!/bin/bash

# Keycloak Authorization Code Flow with Proof Key for Code Exchange (PKCE)
#
# Dependencies:
#
#   'brew install jq pup'
#
#   https://stedolan.github.io/jq/
#   https://github.com/ericchiang/pup
#   sudo wget https://github.com/ericchiang/pup/releases/download/v0.4.0/pup_v0.4.0_linux_amd64.zip | sudo unzip pup_v0.4.0_linux_amd64.zip -d /usr/local/bin 


### ----------------------------

usage()
{
  printf 'Usage  : %s -a %s -r %s -c %s -l %s -u %s\n' "${0##*/}" \
    "<AUTHORITY>" "<REALM>" "<CLIENT_ID>" "<REDIRECT_URL>" "<USERNAME>" "<SECRET>"

  printf 'Example: %s -a "%s" -r "%s" -c "%s" -l "%s" -u "%s" -s "%s"\n' "${0##*/}" \
    "https://keycloak.example.com/auth" \
    "myrealm" \
    "myclient" \
    "https://myapp.example.com/" \
    "myusername" \
    "secret"

  printf '\nAccepts password from stdin, env AUTHORIZATION_CODE_LOGIN_PASSWORD, or prompt.\n'
  exit 2
}

while getopts 'a:r:c:l:u:s:?h' c
do
  case $c in
    a) authority=$OPTARG ;;
    r) realm=$OPTARG ;;
    c) clientId=$OPTARG ;;
    l) redirectUrl=$OPTARG ;;
    u) username=$OPTARG ;;
    s) secret=$OPTARG ;;
    h|?) usage ;;
  esac
done

[[ -z $authority || -z $realm || -z $clientId || -z $redirectUrl || -z $username || -z $secret ]] && usage

password="$AUTHORIZATION_CODE_LOGIN_PASSWORD"
#[[ -z $password ]] && read -rp "password: " -s password

### ----------------------------

base64url() { tr -d '[:space:]' | tr -- '+/' '-_' | tr -d = ; }

sha256sum() { printf "%s" "$1" | openssl dgst -binary -sha256 | openssl base64 -e | base64url ; }

codeVerifier=$(openssl rand -base64 96 | base64url)

cookieJar=$(mktemp ".cookie.jar.XXXX")
trap 'rm "$cookieJar"' EXIT

# printf "start"
loginForm=$(curl -k -sSL --get --cookie "$cookieJar" --cookie-jar "$cookieJar" \
  --data-urlencode "client_id=${clientId}" \
  --data-urlencode "redirect_uri=$redirectUrl" \
  --data-urlencode "scope=openid" \
  --data-urlencode "response_type=code" \
  --data-urlencode "code_challenge=$(sha256sum "$codeVerifier")" \
  --data-urlencode "code_challenge_method=S256" \
  --header 'Authorization: Basic ' \
  "$authority/realms/$realm/protocol/openid-connect/auth" \
  | pup '#kc-form-login attr{action}')
# echo $loginForm
loginForm=${loginForm//\&amp;/\&}
# echo $loginForm
# printf "end"
# printf "start2"
codeUrl=$(curl -k -sS --cookie "$cookieJar" --cookie-jar "$cookieJar" \
  --data-urlencode "username=$username" \
  --data-urlencode "password=$password" \
  --write-out "%{redirect_url}" \
  "$loginForm")
# printf $codeUrl
code=${codeUrl##*code=}
# printf $code
accessToken=$(curl -k -sS --cookie "$cookieJar" --cookie-jar "$cookieJar" \
  --data-urlencode "client_id=$clientId" \
  --data-urlencode "redirect_uri=$redirectUrl" \
  --data-urlencode "client_secret=${secret}" \
  --data-urlencode "code=$code" \
  --data-urlencode "code_verifier=$codeVerifier" \
  --data-urlencode "grant_type=authorization_code" \
  "$authority/realms/$realm/protocol/openid-connect/token" \
  | jq -r ".access_token")

printf "%s" "$accessToken"
