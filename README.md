# Telegram Bot to bypass Short Links, get direct DLs & also Shorten URLs

> # Environment Variables

- `CONFIG_ENV_URL` Put your Config File URL (pasted in Github Gist) so that it works as Bot Config
- `API_HASH` Your API Hash from [my.telegram.org](https://my.telegram.org)
- `API_ID` Your API ID from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` Your bot token from [@BotFather](https://telegram.dog/BotFather)
- `COMMAND_PREFIXES` Prefixes for running Bot Commands. Separate them by space such as "! . /"
- `OWNER_ID` - User ID of the Bot Owner (controls sensitive Bot Information!)
- `SUDO_USERS` Sudo Users who can control the Bot. Separate User IDs by space
- `BOT_USERNAME` Your BotuserName Without `@`. Example `MultiFunctionUse_Bot`
- `BIFM_URL` Your [BIFM](https://git.gay/a/bifm) instance Url. Default to `https://bifm.tacohitbox.com/api/bypass?url`
- `DATABASE_URL` Your Mongo Database URL (Connection string). Follow this [guide](https://github.com/missemily22/MultiFunctionBot/blob/main/README.md#generate-database) to generate database. 
- `LOG_CHANNEL` Your Log Channel ID where the Bot which store Critical Information. Starts with "-"
- `BOTOWNER_UNAME` Username Name of the Bot Owner (without `@`)
- `FORCESUB_ENABLE` Set to True if you want to enable ForceSubscribe else set to False/None
- `FORCESUB_CHANNEL` ID of the Channel you want ForceSubscribe
- `FORCESUB_CHANNEL_UNAME` Username of the Channel you want ForceSubscribe (without `@`)
- `HUBDRIVE_CRYPT` Put your HubDrive Crypt
- `KATDRIVE_CRYPT` Put your KatDrive Crypt
- `KOLOP_CRYPT` Put your Kolop Crypt
- `DRIVEFIRE_CRYPT` Put your DriveFire Crypt
- `DRIVEBUZZ_CRYPT` Put your DriveBuzz Crypt
- `DRIVEHUB_CRYPT` Put your DriveHub Crypt
- `GADRIVE_CRYPT` Put your GaDrive Crypt
- `JIODRIVE_CRYPT` Put your JioDrive Crypt
- `Sharerpw_XSRF` Put your Sharer XSRF Token
- `Sharerpw_laravel` Put your Sharer Laravel Session
- `SHAREDRIVE_PHPCKS ` Put your ShareDrive.pics PHP Packs Token
- `TERABOX_COOKIES_URL` Put your TeraBox Cookies link pasted in Github Gist. Get Cookies in [terabox_cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
- `DEFAULT_UPLOAD_HOST` Put the default host number for File Uploading. See the [table](/README.md#upload-hosts) for more Info
- `UPLOAD_SIZE_LIMIT` Put the Max Size Limit (in GB) for File Upload Function
- `UPTOBOX_TOKEN` Put your UptoBox Account Token (Free Account works too!)
- `EMILY_API_URL` Your [Emily API](https://github.com/missemily22/EmilyAPI) instance Urls. Separate API URLs by space
- `UPSTREAM_REPO` Add the Upstream Repo of your Bot for automatic updation
- `UPSTREAM_BRANCH` Select the Upstream Branch of your Bot for automatic updation
---

<b>NOTE: Fill the above values in <code>config.env</code> or use them as Environment Variables. </b><br>

# BotFather Commands (for Public Users) -
```
start - Bot Start Message
help - Alias command for start
dalle - Generate images from a text prompt using DALLE-Mini
upload - Upload a Telegram File to various Free File Hosting Servers
mediainfo - (or use /m) Generate mediainfo from Telegram files or direct download links
screenshot - (or use /ss) Generates video frame screenshot from Telegram files or direct download links
bifm - Bypass Short Links using BIFM API
direct - Get Direct Link for various Supported URLs
bvip - Bypass Short Links using Bypass.vip API
bypass - Bypass Various Supported Shortened URLs
multi - Bypass Short Links using PyBypass Library
shorten - Get AdFree Shortened URLs of your Link
magnet - Extract Magnet from Torrent Websites
index - Extract Direct Links from Bhadoo Index Folder URLs
scrape - Extract Direct Links from Supported Sites
ytdl - (or /ytdlp) Extract DL Links using YT-DLP
gd - (or use /clone) Get GDrive Links for various Drive File Sharer
headfone - Scrape Headfone.co.in to get Direct Links of an Album
hungama - Get Download link and Metadata of a Hungama Link
image2pdf - Convert Image to PDF
rename - Rename a File in Telegram
tgupload - Upload a File to Telegram
takess - Take ScreenShot of a Webpage
wayback - Generate WayBack of a Webpage
```

<details>
<summary><strong>Basic Bot Commands and it's usage</strong></summary>
<ul>
<br>
	<li>
	<i><b>Users Commands </b></i><br><br>
	/start - To get the start message.<br>
	/help - Alias command for start. <br>
    /dalle - Generate images from a text prompt using DALLE-Mini <br>
    /upload - Upload a Telegram File to various Free File Hosting Servers <br>
    /mediainfo - (or use /m) Generate mediainfo from Telegram files or direct download links <br>
    /screenshot - (or use /ss) Generates video frame screenshot from Telegram files or direct download links <br>
    /bifm - Bypass Short Links using BIFM API <br>
    /direct - Get Direct Link for various Supported URLs <br>
    /bvip - Bypass Short Links using Bypass.vip API <br>
    /bypass - Bypass Various Supported Shortened URLs <br>
    /multi - Bypass Short Links using PyBypass Library <br>
    /shorten - Get AdFree Shortened URLs of your Link <br>
    /magnet - Extract Magnet from Torrent Websites <br>
    /index - Extract Direct Links from Bhadoo Index Folder URLs <br>
    /scrape - Extract Direct Links from Supported Sites <br>
    /ytdl - (or /ytdlp) Extract DL Links using YT-DLP <br>
    /gd - (or use /clone) Get GDrive Links for various Drive File Sharer <br>
    /headfone - Scrape Headfone.co.in to get Direct Links of an Album <br>
    /hungama - Get Download link and Metadata of a Hungama Link <br>
    /image2pdf - Convert Image to PDF <br>
    /rename - Rename a File in Telegram <br>
    /tgupload - Upload a File to Telegram <br>
    /takess - Take ScreenShot of a Webpage <br>
    /wayback - Generate WayBack of a Webpage <br>
    /paste - Paste the text/document to KatBin <br>
	/ping - Ping the telegram api server <br>
	</li>
<br>
    <li>
    <i><b>Sudo User Commands </b></i><br><br>
    /db: Get information about Bot DataBase <br>
    /speedtest: Check the internet speed of bot server.<br>
    /serverstats: Get the stats of server.<br>
    /stats: Alias command for serverstats.<br>
    /users - Get details about the Bot Users <br>
    /inspect - Inspect the message and give reply in json format <br>
    </li>
<br>
    <li>
    <i><b>Developer Commands </b></i><br><br> 
	/addsudo - Add a user to the Bot sudo users list <br>
    /removesudo - Remove a user to the Bot sudo users list <br>
    /broadcast - Broadcast a message to all the Bot Users <br>
    /shell: To run the terminal commands via bot.<br>
    /exec: (or use /py) To run the python commands via bot. <br>
    /update: To update the bot to latest commit from UpStream Repository. <br> 
    /restart: Restart the bot. <br>
    /log: To get the log file of bot. <br>
</ul>
</details>
<br> 

------

### Generate Database

1. Go to `https://mongodb.com/` and sign-up.
2. Create Shared Cluster.
3. Press on `Database` under `Deployment` Header, your created cluster will be there.
5. Press on connect, choose `Allow Access From Anywhere` and press on `Add IP Address` - Put '0.0.0.0', then create user.
6. After creating user press on `Choose a connection`, then press on `Connect your application`. Choose `Driver` **python** and `version` **3.6 or later**.
7. Copy your `connection string` and replace `<password>` with the password of your user, then press close.

------

## Upload Hosts

| #  |     Host    |  Limit |
|----|-------------|--------|
| 1  | anonfiles   | 20 GB  |
| 2  | Catbox      | 200 MB |
| 3  | file.io     | 2 GB   |
| 4  | Filemail    | 5 GB   |
| 5  | Gofile      | unlim  |
| 6  | KrakenFiles | 1 GB   |
| 7  | LetsUpload  | 10 GB  |
| 8  | MegaUp      | 5 GB   |
| 9  | MixDrop     | unlim  |
| 10 | pixeldrain  | 10 GB  |
| 11 | Racaty      | 10 GB  |
| 12 | transfer.sh | unlim  |
| 13 | Uguu        | 128 MB |
| 14 | WeTransfer  | 2 GB   |
| 15 | workupload  | 2 GB   |
| 16 | zippyshare  | 500 MB |


# Contributions - 
- Thanks to [Sanjit Sinha](https://github.com/sanjit-sinha) for [Telegram-Bot-Boilerplate](https://github.com/sanjit-sinha/Telegram-Bot-Boilerplate) Template and [Tg-MediaInfoBot](https://github.com/sanjit-sinha/Tg-MediaInfoBot)
- Thanks to [Altryne](https://github.com/altryne) for [ChatGPT-Telegram-Bot](https://github.com/altryne/chatGPT-telegram-bot)
- Thanks to [Yukki Senpai](https://github.com/xcscxr) for Bypassers as well as GDrive Sharer Directs
- Thanks to [Jack](https://github.com/JohnWickKeanue) for Site Scraping Scripts
- Thanks to [Miss Emily](https://github.com/missemily22) for maintaining the Repo as well as the API
- Thanks to [zevtyardt](https://github.com/zevtyardt/lk21) for LK21 Bypasser
- Thanks to [Disha Patel](https://github.com/dishapatel010) for ArtStation, MDisk and WeTransfer Direct link Gen
- Thanks to [Bipin Krishna](https://github.com/bipinkrish) for OlaMovies, IGG Games and FileCrypt Site Scrapers

# Deployment

## ⚛️ Deploying on Heroku
- Click on the Button below to deploy this Bot to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/missemily22/MultiFunctionBot)


<a name="deploy-to-koyeb"></a>

<h2> <b><img src="https://user-images.githubusercontent.com/87380104/205833766-633843a2-d802-4c72-8732-70d826d5c144.png" height="20" width="20">  Deploy on Koyeb</b> </h2>

<b>Run program totally for free on Koyeb with single click deployment button!</b>
#### **1. Click the following one-click deployment button:**
[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/apps/deploy?type=docker&image=ghcr.io/missemily22/multifunctionbot:lite&name=mfbot&ports=8080;http;/&env[CONFIG_ENV_URL]=Put-your-Config-File-URL-so-that-it-works-as-Bot-Config)
#### **2. Fill the Config File variable with a direct link to your config and click `Deploy`.**
#### **3. While deployment, you can choose `Micro` instance type since it requires 512 RAM.**
![image](https://user-images.githubusercontent.com/87380104/205841570-6a43c020-eecf-4574-8c53-41f9454b5d79.png)
#### **⛔NOTE: This method uses ready-to-use Docker Image made specially for Koyeb, hence any change requires building of new image with `Flask` to listen on port `8080`.**


<!---Docker--->
<h2><b>🐳Build or Deploy using Docker</b></h2>
<p><b>MultiFunctionBot can be deployed almost everywhere using Docker</b></p>
<h4><b>1.To pull MultiFunctionBot Docker Image:</b></h4>
<p><b>-><code>docker pull ghcr.io/missemily22/multifunctionbot:main</code></b></p>
<h4><b>2.Or, to use as base Image:</b></h4>
<p><b>-><code>FROM ghcr.io/missemily22/multifunctionbot:main</code></b></p>
<p><b>⛔NOTE:</b></p>
<p><b>Docker Image only accepts the variables as stated before</b></p>
<p><b>Fly.io is platform and best alternative of Heroku (Salesforce) becuase here you can deploy your apps by just adding Credit Card (without being charged) or anyother payment methods, unlike Heroku, they offers you 2,340 running hours per month	while Heroku only provides 550 running hours (dyno hours) to run your app! that means you don't have to worry about suddenly getting your app stopped like in the case of Heroku. Fly.io also not restarts your app each 24 hours which enables you to clone bigger data easily.</b></p>
<h4><b>1.Create an account on <a href="https://fly.io/app/sign-in">Fly.io</a>.</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/186624984-a8a4e199-3f04-4456-a9a0-47a05e5632ba.png">
<h4><b>2.Install flyctl on your system.</b></h4>
<p><b><i>MacOS / Linux:</i></b></p>
<p><b><code>curl -L https://fly.io/install.sh | sh</code></b></p>
<p><b><i>Using Brew:</i></b></p>
<p><b><code>brew install flyctl</code></b></p>
<p><b><i>Windows Powershell:</i></b></p>
<p><b><code>iwr https://fly.io/install.ps1 -useb | iex</code></b></p>
<p><b><i>Termux:</i> (Refer <a href="https://github.com/TheCaduceus/CloneBot_V2/discussions/54">#54</a>)</b></p>
<p><b><code>pkg install flyctl</code></b></p>
<h4><b>3.Download MultiFunctionBot Repository:</b></h4>
<p><b><code>git clone https://github.com/missemily22/MultiFunctionBot</code></b></p>
<h4><b>4.Now run following commands:</b></h4>
<p><b>
<code>cd MultiFunctionBot</code> - To change directory.</br>
<code>fly auth login</code> - To login on Fly.io.</br>
<code>fly launch</code> - To configure basic things, like app name and data center as well as creating <code>fly.toml</code>.
</b></p>
<h4><b>5.Configure App:</b></h4>
<p><b>1.For app name keep the field empty (Hit <code>Enter</code>), and for choosing data center! use arrow keys to select one. For attaching Postgres Database enter
<code>N</code> including for Deploy Now.</b></p>
<p><b>2.Once you run the above command! It will say <code>fly.toml</code> file exists, open the <code>fly.toml</code> file with any text editor and under <code>[env]</code> section put your Env Variables !</b></p>
<img src="https://user-images.githubusercontent.com/114487400/197971480-44347f22-f297-4fe1-8f74-c86700e93342.png">
<p><b>3.Everything done! now run the final deploy command to deploy your app.</b></p>
<p><b><code>fly deploy</code> - To deploy your app.</b></p>
<p><b>⛔NOTICE: <br> 1. You can use <code>flyctl</code> instead of <code>fly</code>.<br>2. Choose yes to Use Exisiting Configurtion to avoid loss of fly.toml file </b></p>

<h2><b>♦️Deploy on Clever Cloud</b></h2>
<p><b>Clever Cloud is a Europe-based PaaS (Platform as a Service) company. They help developers deploy and run their apps with bulletproof infrastructure, automatic scaling as well as fair pricing. In my opinion! it is best choice to deploy MultiFunctionBot on Clever Cloud because pricing is excellent & fair as well as you can run MultiFunctionBot for days to clone large amount of data.</b></p>
<p><b>⛔NOTICE: Before deploying/running MultiFunctionBot on Clever Cloud! Don't forget to add payment method like credit card in your account to verify your account otherwise deploying and using MultiFunctionBot on Clever Cloud will cause suspension of your app/account.</b></p>
<h4><b>1.First log in on <a href="https://www.clever-cloud.com">Clever Cloud</a>.</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/184601649-db7a14f5-9eb0-4da8-8709-32f58a339c09.png">
<h4><b>2.Now click on <code>Create</code> and then select <code>an application</code> from the list.</b></h4>
<img src="https://user-images.githubusercontent.com/114487400/197973189-d96996b8-779e-47b9-b3e3-9030d472842e.png">
<h4><b>3.Once you reach "Application Creation" page, choose "Create an application from GitHub repository" and select the MultiFunctionBot Repository. Not visible? fork this!</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/184602864-f01c6b56-0fe5-4360-9e26-531e8aea2cef.png">
<h4><b>4.Done? now specify the application type by choosing our beloved <code>Docker</code>.😘</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/184603233-e4427ea0-fce6-4420-85bf-4b4fb0660005.png">
<h4><b>5.After that! directly click <code>Next</code> on "How many number of instances?" page and keep the number of instance only 1. Additionally, you can keep instance type to <code>Nano</code> which is most cheap because MultiFunctionBot is designed to run on very low end systems.</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/184603755-cf8f55a6-2c41-4112-b24c-22fb36878479.png">
<h4><b>6.Provide your instance a beautiful name, it can be "MultiFunctionBot" itself, and for instance location, you can choose <code>Paris France</code> for lower ping (tested!😉).</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/184604532-d1e3db06-1778-482c-a0d8-bd41cc5dbe1d.png">
<h4><b>7.Now it will navigate to "Add-ons" page, simply click <code>I DON'T NEED ANY ADD-ONS</code> because... you already know it!🌟 still why? it is designed for low end systems.</b></h4>
<img src="https://user-images.githubusercontent.com/87380104/184605060-83283c09-043b-475e-90ca-a9e4ad315a71.png">
<h4><b>8.Then enter <b> Environment Variables</b> one by one and Clever Cloud will start deploying your instance.</b></h4>
<img src="https://user-images.githubusercontent.com/114487400/198011503-68fb8981-a18e-4ba6-b7e3-415c7c7c223a.png">
<h4><b>9.Finally! to check if MultiFunctionBot is working perfectly, you can open the domain (it will display the guide) provided by Clever Cloud for your instance which can be collected from <code>Domain Names</code> tab and for logs you can check <code>Logs</code> tab.</b></h4>
<img src="https://user-images.githubusercontent.com/114487400/198011888-9ee2949c-e5e3-43ce-a6a1-a1b20d806fa4.png">
<!---Okteto--->
<h2><b>🪬Deploy on Okteto</b></h2>
<p><b>Okteto is Kubernetes development platforms and used by many users and it is ideal for lightweight apps and it is perfect for MultiFunctionBot, Okteto is worst than Heroku, your bot will sleep after 24 hours and will not get back to online until you ping the provided ENDPOINT.</b></p>
<h4><b>1.First Create your Okteto Account, You need one GitHub account as okteto supports only one Method to either Create or Login:<a href="https://cloud.okteto.com/#/login" alt="Login on Okteto"> Create/Login on Okteto</a></b></h4>
<h4><b>2.Now fork this repository, and go to Okteto Dashboard then press "Launch Dev Environment".</b></h4>
<h4><b>3.After it, select your forked repository and select branch <code>main</code> and add following value carefully:</b></h4>
<p><b>
	Add your <code>Environment Variables</code> one by one
</b></p>
<h4><b>4.Once done! press "Launch" and you successfully done it! Yes 😊</b></h4>
<h4><b>5.Okteto make your deployed app to sleep if provided ENDPOINT (Allotted URL) remain untouched for 24 Hours. So lets setup a simple cron-job to keep your app active.</b></h4>
<h4><b>6.First copy your app's ENDPOINT as shown in the image and go to <a href="https://cron-job.org/en" alt="Cron-Job">Cron-Job.org</a> and sign up!</b></h4>
<h4><b>7.Done? Nice! now click "CREATE CRONJOB" button and provide your copied ENDPOINT URL that you just copied and change execution schedule to every 5 minutes.Finally! click "CREATE" and you done it! 😌 Relax and use MultiFunctionBot freely.</b></h4>
<p><b>⛔NOTE: Don't forget to setup Cron-Job for Okteto otherwise your deployed bot will go into sleep and you have to active it from Okteto Dashboard, while Cron-Job doing it on your behalf.</b></p>
<!---Deploy-on-VPS/PC--->
<h2><b>🖥️ Deploy on VPS or PC</b></h2>
<p><b>Running MultiFunctionBot on your PC or VPS is very simple and takes very less efforts! It have very less load on your System and don't use your bandwidth or Internet connection for cloning Google Drive data but only for calling Telegram APIs to update the progress or to generate required response.</b></p>
<h4><b>1.Download Requirements:</b></h4>
<p><b>
	-><a href="https://www.python.org/downloads/">Python 3 or above with pip</a><br>
	-><a href="https://git-scm.com/downloads">Git</a>
</b></p>
<h4><b>2.Download Repository:</b></h4>
<p><b>
	-><code>git clone https://github.com/missemily22/MultiFunctionBot</code><br>
</b></p>
<h4><b>3.Install MultiFunctionBot Requirements:</b></h4>
<p><b>
	-><code>cd MultiFunctionBot</code><br>
	-><code>pip install -r requirements.txt</code>
</b></p>
<h4><b>4.Edit <code>Config.ini</code> file</b></h4>
<p><b>
	->Rename<code>sample_config.env</code> to <code>config.env</code> and open the file in any text editor and enter the values of variables as described <br>
</b></p>
<h4><b>5.Start MultiFunctionBot:</b></h4>
<p><b>
      -><code>cd MultiFunctionBot</code><br>
      -><code>python -m bot</code>
</b></p>
<h4><b>6.Stop MultiFunctionBot:</b></h4>
<p><b>
	->Press <code>CTRL</code> + <code>C</code> keys
</b></p>

## Note:
- I will soon add other Deployment Methods!

### Credits
- Bot is purely based on [Disha Patel](https://github.com/dishapatel010) [MMBot](https://github.com/dishapatel010/mmbot)