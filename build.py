#!/bin/python3
import json, os, sys, datetime

# load all the json info, create docs dir
siteInfo = json.load(open("site.json"))
os.system("rm -rf docs")
os.system("mkdir -p docs/support docs/privacy")

# fill out urls for each app that doesn't have one
for app in siteInfo["apps"]:
    if "url" not in app:
        app["url"] = f"/apps/{app['id']}"
        app["target"] = ''
    else:
        app["target"] = 'target="_blank"'

def loadPiece(name):
    return open(f"pieces/{name}.newt.html").read()

def replaceVars(template, vars):
    for key in vars:
        varContent = vars[key]
        if type(varContent) == list:
            varContent = "\n".join(varContent)
        varContent = str(varContent)
        template = template.replace("{{" + key + "}}", varContent)
    return template

# Our goal is to construct the home page, so first let's grab the root page
index = loadPiece("index")

# start building the vars to replace on the home page, which include about, studios, and apps
about = loadPiece("about")

# list of studios
studioPiece = loadPiece("studio")
studios = replaceVars(loadPiece("studios"), {
    "studios": [replaceVars(studioPiece, studio) for studio in siteInfo["studios"]]
})

# same thing but for apps
appPiece = loadPiece("appicon")
featuredIdxMap = {}
for x, s in enumerate(siteInfo["featured"]):
    featuredIdxMap[s] = x

featuredApps = filter(lambda app: app["id"] in featuredIdxMap, siteInfo["apps"])
featuredApps = sorted(list(featuredApps), key=lambda app: featuredIdxMap[app["id"]])
apps = replaceVars(loadPiece("apps"), {
    "apps": [replaceVars(appPiece, app) for app in featuredApps]
})

root_frame = replaceVars(loadPiece("root"), {
    "indexContent": loadPiece("index"),
    "currentYear": datetime.datetime.now().year
})

# main home page, no return and three contents
index = replaceVars(root_frame, {
    "title": "Home",
    "pageContent": [about, studios, apps],
    "returnLink": ""
})
open("docs/index.html", "w").write(index)

# now we will build the privacy and support pages
privacyIdxMap = {}
for x, s in enumerate(siteInfo["privacylist"]):
    privacyIdxMap[s] = x

privacyApps = filter(lambda app: app["id"] in privacyIdxMap, siteInfo["apps"])
privacyApps = sorted(list(privacyApps), key=lambda app: privacyIdxMap[app["id"]])
listPiece = loadPiece("listentry")
listentries = [replaceVars(listPiece, entry) for entry in privacyApps]

returnPiece = loadPiece("return")

privacy = replaceVars(root_frame, {
    "title": "Privacy",
    "pageContent": replaceVars(loadPiece("privacy"), {
        "privacyAppList": listentries
    }),
    "returnLink": returnPiece
})
open("docs/privacy/index.html", "w").write(privacy)

support = replaceVars(root_frame, {
    "title": "Support",
    "pageContent": loadPiece("support"),
    "returnLink": returnPiece
})

open("docs/support/index.html", "w").write(support)

# create an apps folder and page for each app
for app in siteInfo["apps"]:
    if "long_desc" in app:
        app["long_desc"] = [f"<p>{a}</p>" for a in app["long_desc"]]
    else:
        app["long_desc"] = "<p>Work in progress, more information coming soon.</p>"
    if "details" not in app:
        app["details"] = "<a href=" + app["url"] + " target='_blank'>Visit Site</a>"
        app["long_desc"] = "<p>Info on this app is available on the app's external website, which can be found through the link above.</p>"
    appPage = replaceVars(root_frame, {
        "title": app["name"],
        "pageContent": replaceVars(loadPiece("appdetails"), app),
        "returnLink": returnPiece
    })
    os.system(f"mkdir -p docs/apps/{app['id']}")
    open(f"docs/apps/{app['id']}/index.html", "w").write(appPage)


# build main app page
allApps = replaceVars(loadPiece("apps"), {
    "apps": [replaceVars(appPiece, app) for app in siteInfo["apps"]]
})

allApps = replaceVars(root_frame, {
    "title": "Apps",
    "pageContent": allApps,
    "returnLink": returnPiece
})

open("docs/apps/index.html", "w").write(allApps)

# link in the css file
os.system("cp style.css docs/style.css")

# copy the images
os.system("cp -r images docs/images")