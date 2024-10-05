# Home Assistant - SMHI Weather Warnings & Alerts

## Overview

Easily receive and manage SMHI (Swedish Meteorological and Hydrological Institute) weather warnings and alerts directly in Home Assistant, enabling you to trigger actions or display information on your dashboard.

There is also a dashboard card specifically for this integration, which can be found here: [SMHI Alert Card](https://github.com/Nicxe/home-assistant-smhialert-card)

This custom component connects to SMHI's open API to retrieve weather alerts in Sweden, organizing the data by districts and their respective messages. You can choose to receive notifications for all districts or for a specific one.


*Based on [SMHI Alert Card](https://github.com/Lallassu/smhialert)*

## Installation

You can install this custom component using [HACS](https://www.hacs.xyz/) as a custom repository by following this guide:

1. Click on the 3 dots in the top right corner of the HACS overview menu.
2. Select "Custom repositories".
3. Add the URL to the repository: ```https://github.com/Nicxe/home-assistant-smhialerts```
4. Select type: Integratin
5. Click the "ADD" button.


<details>

<summary>**Manual Installation** *(without HACS)*</summary>
1. Download the latest release of the SMHI Alert integration from [GitHub Releases](https://github.com/Nicxe/home-assistant-smhialerts/releases).
2. Extract the downloaded files and place the smhialert folder in your Home Assistant custom_components directory (usually located in the config/custom_components directory).
3. Restart your Home Assistant instance to load the new integration.

</details>


## Example Configuration

Add the following to your `configuration.yaml` file in Home Assistant:

### Receive Alerts for All Districts

```yaml
sensor:
  - platform: smhialert
    district: 'all'
    language: 'sv'
```

### Receive Alerts for a Specific District

```yaml
sensor:
  - platform: smhialert
    district: '9'
```

The sensor provides information in English by default. To get the information in Swedish, add `language: 'sv'` to your configuration.

Available districts:
```
1   Stockholms län  
3   Uppsala län  
4   Södermanlands län  
5   Östergötlands län  
6   Jönköpings län  
7   Kronobergs län  
8   Kalmar län  
9   Gotlands län  
10  Blekinge län  
12  Skåne län  
13  Hallands län  
14  Västra Götalands län  
17  Värmlands län  
18  Örebro län  
19  Västmanlands län  
20  Dalarnas län  
21  Gävleborgs län  
22  Västernorrlands län  
23  Jämtlands län  
24  Västerbottens län  
25  Norrbottens län  
41  Bottenviken  
42  Norra Kvarken  
43  Norra Bottenhavet  
44  Södra Bottenhavet  
45  Ålands hav  
46  Skärgårdshavet  
47  Finska Viken  
48  Norra Östersjön  
49  Mellersta Östersjön  
50  Rigabukten  
51  Sydöstra Östersjön  
52  Södra Östersjön  
53  Sydvästra Östersjön  
54  Bälten  
55  Öresund  
56  Kattegatt  
57  Skagerrak  
58  Vänern  
```

## Usage Screenshots
Using the [SMHI Alert Card](https://github.com/Nicxe/home-assistant-smhialert-card)

<img src="https://github.com/Nicxe/home-assistant-smhialert-card/blob/main/Screenshot.png">