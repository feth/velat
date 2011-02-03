DIRS = "src/velat"

all:
	for dir in $(DIRS); do make -C $$dir $@; done

clean:
	for dir in $(DIRS); do make -C $$dir $@; done
