fs			= require('fs')
path		= require('path')
{exec}		= require('child_process')

Cakefile		= 'Cakefile'
BASE			= 'viewer'
COFFEEINDIR		= "#{BASE}/static/coffee"
COFFEEOUTDIR	= "#{BASE}/static/debug"
JSOUTDIR		= "#{BASE}/static/js"
LESSINDIR		= "#{BASE}/static/less"
LESSINFILES		= [
	['bootstrap/bootstrap.less','bootstrap.css']
	['main.less','main.css']
]
LESSOUTDIR		= "#{BASE}/static/css"
TMPDIR			= 'tmp'


compile_coffee=(cb)->
	console.log(">coffee -o #{JSOUTDIR}/ -c #{COFFEEINDIR}/")
	exec("coffee -o #{JSOUTDIR}/ -c #{COFFEEINDIR}/", (err, stdout, stderr)->
		if stderr or err then console.log(err, stderr)
		cb(null)
	)
compile_less=(cb)->
	OPENCHILDREN=0
	for file in LESSINFILES
		OPENCHILDREN+=1
		console.log(">lessc #{LESSINDIR}/#{file[0]} #{LESSOUTDIR}/#{file[1]}")
		exec("lessc #{LESSINDIR}/#{file[0]} #{LESSOUTDIR}/#{file[1]}", (err, stdout, stderr)->
			if stderr or err then console.log(err, stderr)
			OPENCHILDREN-=1
			if OPENCHILDREN==0
				cb(null)
		)

task('build', ->
	compile_less(()->)
	compile_coffee(()->)
)
