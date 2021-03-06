

  
  

# BTicino Smarther integration for Home Assistant

Hi! This project is developed and maintenance by a small community of passionate people who make this solution available for free. 
Special thanks to `@danye72, @Veuchez, @malesci` that are part of this community.

This project want to help Home Assistant users to integrate easily **BTicino Smarther X8000**

[![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)

# Preparation
To install the integration you need some prerequisite done

## 1. Legrand cloud part

### 1.1. Register a Developer account
Sign up for a new Developer account on Works with Legrand website (https://developer.legrand.com/login).

### 1.2. Subscribe to Legrand APIs
Sign in, go to menu `API > Subscriptions` and make sure you have `Starter Kit for Legrand APIs` subscription activated; if not, activate it.

![legrand1](https://user-images.githubusercontent.com/36844281/117118588-3b331a00-ad91-11eb-969f-6e1cd0548972.PNG)

### 1.3. Register a new application
Go to menu `User > My Applications` and click on `Create new` to register a new application:
- Insert a **valid public URL** of your Home Assistant in "First Reply Url"
- Make sure to tick the checkbox near scopes `comfort.read` and `comfort.write`
```
Public Url = https://github.com/danye72/smarther-v1
```
```
First Reply Url = http://myHALocalIP/callback  Ex. http://192.168.1.10/callback
```
![register app](https://user-images.githubusercontent.com/36844281/117126831-9bc75480-ad9b-11eb-8fa9-76b0ef361513.png)

Submit your request and wait for a response via email from Legrand (it usually takes 1-2 work days max).
If your app has been approved, you should find in the email your **Client ID** and **Client Secret** attributes.

# Installation
Once you completed app registration phase having received  **Client ID** and **Client Secret** attributes, you can proceed with the **first installation**. 

## 2. Configuration

### 2.1. Get your Code

 1. Compose an URL from this base https://partners-login.eliotbylegrand.com/authorize?client_id=xxxx&response_type=code&redirect_uri=yyyy where **xxxx** is your **Client ID** and **yyyy** is the address of your web application registered on the Legrand site in **First Reply Url** field
 2. Open a browser and search for the URL just mentioned
 3. Login with your developer account

 ![login](https://user-images.githubusercontent.com/36844281/117126661-5dca3080-ad9b-11eb-9a48-588dc5b3903c.PNG)

 4. Allow your app permissions by clicking **Accept**

 ![app permissions](https://user-images.githubusercontent.com/36844281/117126684-67ec2f00-ad9b-11eb-8f71-27fd35ca7451.PNG)

 5. Get **code key** from the address bar of the browser (very long string)
 
 ![get code](https://user-images.githubusercontent.com/36844281/117126696-6d497980-ad9b-11eb-9da5-986dea7d82c1.PNG)

> **Note**: Once the code is obtained, you must complete the remaining steps until the Home assistant restarts in a short time otherwise the **code expires** and must be regenerated by repeating point 2.1. Get your Code.

### 2.2. Store your secrets in Home Assistant

#### Secret variables

These are the variables to add in your secrets file

| Secret key                          | How to get                        | Format
|-------------------------------------|-----------------------------------|-
|`bticino_thermostat_client_id` | received via email | xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
|`bticino_thermostat_client_secret` | received via email | **********************************
|`bticino_thermostat_subscription_key` | primary key from Legrand subscription | xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
|`bticino_thermostat_code` | get in browser from the previous step | *[very long string]*
|`bticino_thermostat_name` | name of the thermostat in BTicino App | string *[comma separated list in case of multiple thermostat, uppercases and spaces are allowed]*
|`domain` | public Home Assistant URL | string
|`bticino_thermostat_prerelease` | optional | boolean

> **Note**: In case you Home Assistant server is placed at your home, make sure to have port forwarding properly configured in your home modem/router in order that public Home Assistant URL address is be reachable from Legrand!

#### Update your Secrets file with the variables
Add the following lines in your Home Assistant secrets file placed in `/config/secrets.yaml`

>Replace values with your (here are just for example)!
```
bticino_thermostat_client_id: e9d1c3c5-a7e0-4f00-a8e2-6f402f919953
bticino_thermostat_client_secret: qT128rk4~o_V.O_-Do-tOHO7W07X5w6v3~
bticino_thermostat_subscription_key: 5bc08c57bf24458ab8c155fc37cf955c
bticino_thermostat_code: [very long string]
bticino_thermostat_name: mydevice1, My Device2
domain: mydomain.duckdns.com [specify the port if is not standard 443]
bticino_thermostat_prerelease: false
```

### 2.3. Allow HA to include packages on configuration file
Add the following lines in your Home Assistant configuration file placed in `/config/configuration.yaml`

- This example for allow all the yaml files under the folder `/config/packages`
```
homeassistant:
  ...
  packages: !include_dir_named packages
```

- Alternatively, if you wish you can allow specific yaml file in this way:
```
homeassistant:
  ...
  packages:
    package_1: !include packages/smarther/smarther_<<thermostat_name>>.yaml
    package_2: !include packages/smarther/smarther_webhooks.yaml
    package_3: !include packages/smarther/smarther_update.yaml
```

## 3. First run
> Next updates will be done by Home Assistant script, no need to clone and run install command every time, just the first time.
> 
### 3.1. Open a terminal in Home Assistant
Open a shell in Home Assistant.

- for HASSOS or HA supervised installation you can use addon like "*SSH & Web Terminal*"
- for HA core you can exec into the docker container (usually with command like `docker exec -it <container name> /bin/bash` to get a bash shell)

### 3.2. GitHub download latest released version & Run install command 

For  **STABLE** version (**GitHub Release**)
```
gh_repo="danye72/smarther-v1" \
&& curl -s "https://raw.githubusercontent.com/$gh_repo/master/script/init" | bash -s -- --repo $gh_repo
```

For **INCUBATOR** version (**GitHub Prerelease**)
```
gh_repo="danye72/smarther-v1" \
&& curl -s "https://raw.githubusercontent.com/$gh_repo/master/script/init" | bash -s -- --repo $gh_repo --prerelease
```

For new subscription request, add **--subscribe** argument
```
gh_repo="danye72/smarther-v1" \
&& curl -s "https://raw.githubusercontent.com/$gh_repo/master/script/init" | bash -s -- --repo $gh_repo --subscribe
```

![1install](https://user-images.githubusercontent.com/36844281/120300089-e620f000-c2cb-11eb-923b-c8a9c560d55e.PNG)
![1install-end](https://user-images.githubusercontent.com/36844281/120300094-e7eab380-c2cb-11eb-992c-a1725d2455ce.PNG)

### 3.3. Validate HA configuration and Restart
![validate reboot](https://user-images.githubusercontent.com/36844281/117128047-31afaf00-ad9d-11eb-9574-6e2e93b214e4.PNG)

## 4. Lovelace card
> The Lovelace card can be added **manually** or it possible to have new **Lovelace view** that includes one card per Thermostat can be **automatically installed and updated**.

### 4.1 Commons steps: Card dependencies
Install the following Frontends with **HACS**: 
 - layout-card
 - bar-card
 - stack-in-card
 - button-card
 - apexcharts-card
 - card-mod
 - config-template-card

### 4.2. Add Lovelace card manually

#### 4.2.1 Get Lovelace Card for your thermostat
Copy the manual card code from the generated file/files placed in `/config/smarther/lovelace/thermostat_card_<<thermostat_name>>.yaml`

#### 4.2.1 Create manual card
Create a manual card on your favorite Home Assistant view, and past-in the upper mentioned card code.

### 4.3. Activate automatic installation for Lovelace card
A dedicated dashboard will be created for Smarther Thermostat, however lovelace must be set in **yaml mode**.

In the most common case, since many prefer to use the simpler **storage mode**, the latest versions of Home Assistant (> 0.107) help us thanks to the possibility of creating multiple dashboards in parallel in mixed mode.

#### 4.3.1 Enable Lovelace storage mode
So let's modify the ***configuration.yaml*** file in order to have the main dashboard in storage mode, and the one dedicated to Thermostat in yaml mode:

    lovelace:
      mode: storage
      dashboards:
        lovelace-smarther:
          mode: yaml
          title: Thermostats
          icon: mdi:home-thermometer
          show_in_sidebar: true
          filename: /config/smarther/lovelace/smarther_dashboard.yaml

> note:  adjust `/config/smarther` path in case you customized it

The previous configuration as mentioned makes sure to use the storage mode as the main one.

# Runtime
Once you completed all the installation and configurations steps, You have *BTicino Smarther integration for Home Assistant* up and running

## 5. Update
In order to get and install future updates, you can just run the script in Home Assistant called **script.update_from_smarther_github_repo**, already integrated as button in to the lovelace card.
