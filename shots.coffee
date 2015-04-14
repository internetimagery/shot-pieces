# Utility script that grabs Animation Metadata from shotpieces
# node <script> <maya-file>

fs = require 'fs'

if process.argv.length is 3
	path = process.argv[2]
	fs.readFile path, { encoding: "utf-8", flag: "r" }, (err, data)->
		console.log err if err
		re = /fileInfo\s+("|')(shot_piece_[\d]+)\1\s+("|')({.*?})\3\s*;/g
		obj = {}
		while (result = re.exec(data))?
			obj[result[2]] = JSON.parse(result[4].replace(/\\"/g, "\""))
		console.log obj
else
	console.log "Please provide a file to parse. :)"