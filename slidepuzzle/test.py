#!/usr/bin/python

import sys

def dostuff(this=sys.argv):
	if len(this) < 2:
		this = "bullshit"
	else:
		this = sys.argv[1:]

	print this


def main():
	dostuff()


if __name__ == "__main__":
	main()