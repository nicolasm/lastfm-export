#!/bin/bash -
liquibase --logLevel DEBUG --changeLogFile db-changelog.xml --classpath=sqlite-jdbc-3.30.1.jar --driver=org.sqlite.JDBC --url="jdbc:sqlite:lastfm.sqlite" update
