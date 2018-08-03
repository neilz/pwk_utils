# pwk_utils

Util scripts I wrote while taking the [Offensive Secutity: Pentesting with Kali](https://www.offensive-security.com/information-security-training/penetration-testing-training-kali-linux/) course

### cracker.py
Submit NTLM hashes to http://cracker.offensive-security.com and retrieve results
```
> python3 ./cracker.py 0000 - < hashdump.txt
```

### ftp_check.py
Validate credentials against an ftp server
```
> python3 ./ftp_check.py ftp.domain.local --stdin < ftp_creds.txt
```


### payload_gen.py
Generate and (optionally) host reverse shell executables from msfvenom
```
> python3 ./payload_gen tap0 -l 80
```
