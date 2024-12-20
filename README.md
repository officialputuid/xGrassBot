# xGrassBot
This bot connects via multiple HTTP proxies to farm Grass Airdrop Season 2 using a single account. It automatically removes faulty proxies (on/off) and uses the Grass Desktop Node to double the farming points (x2.0).

## Installation

1. Install ENV
   ```bash
   sudo apt update -y && apt install -y python3 python3-venv pip
   ```

2. Setup resources:
   ```bash
   git clone https://github.com/officialputuid/xGrassBot && cd xGrassBot
   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   python3 main.py
   ```

## User ID
- If you haven't registered, feel free to use my referral link: ([REGISTER GRASS](https://app.getgrass.io/register/?referralCode=rjztRGaBttAB6Cx)).
- How to Get Your User ID?
  - Login and open https://app.getgrass.io/dashboard
  - Open Developer Tools in your browser (F12) / Inspect Element.
  - In the "Console" tab, type:
   `localStorage.getItem('userId');`
  - Copy the result without "" or '' and paste it into `uid.txt`.
  - For multiple accounts, add each uid on a new line, for example:
       ```
     uid1
     uid2
     uid2
     ```

## Proxy  
- Fill in `proxy.txt` with the format `protocol://user:pass@host:port`.  
- Adjust the number of proxies to use on the following line `36 "ONETIME_PROXY = 100"`

## Need Proxy?
1. Sign up at [Proxies.fo](https://app.proxies.fo/ref/849ec384-ecb5-1151-b4a7-c99276bff848).
2. Go to [Plans](https://app.proxies.fo/plans) and only purchase the "ISP plan" (Residential plans don’t work).
3. Top up your balance, or you can directly buy a plan and pay with Crypto!
4. Go to the Dashboard, select your ISP plan, and click "Generate Proxy."
5. Set the proxy format to `protocol://username:password@hostname:port`
6. Choose any number for the proxy count, and paste the proxies into `proxy.txt`.

## Donations
- **PayPal**: [Paypal.me/IPJAP](https://www.paypal.com/paypalme/IPJAP)
- **Trakteer**: [Trakteer.id/officialputuid](https://trakteer.id/officialputuid) (ID)
