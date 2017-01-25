#!/usr/bin/make -f

########################################################################
### makefile
### F. Gerstmayer 2016
### UAS Technikum Wien, Embsys, SAT
########################################################################

### DEFAULT COMMANDS
MKDIR		= mkdir -p
COPY		= cp -r
REMOVE		= rm -rf --preserve-root
CHMOD		= chmod
LINK		= ln -s -f
TAR			= tar cvzf
ECHO		= @echo
DATE		= $(shell date +"%Y%m%d")
GIT_REV		= $(shell git rev-list --count master)

### DEFAULT SCRIPT SETTINGS
DEV			= Florian Gerstmayer
EMAIL		= florian.gerstmayer@technikum-wien.at
NAME 		= dot2json
SCRIPT		= $(NAME).py
ARCHIVE		= .tar.gz
DEPENDENCY	= dep/
FILES	        = linkurious.js/build/sigma.js
FILES	       += linkurious.js/build/plugins/sigma.parsers.json.min.js
FILES	       += linkurious.js/build/plugins/sigma.renderers.edgeLabels.min.js
FILES	       += linkurious.js/build/plugins/sigma.plugins.dragNodes.min.js
EXPORT		= export/
DIRNAME 	= $(NAME)/
OTHER		= out/
RELEASE		= release/
MAJOR		= 1

#$(DATE)-
REL_NAME	= $(NAME)-$(MAJOR).$(GIT_REV)
CFG			= $(RELEASE)$(REL_NAME)/DEBIAN/control
ARCH		= $(RELEASE)archiv/

### INSTALL DIRECTORY (modify if necessary)
# /usr/ /usr/bin/ /bin/
USRBIN		= /usr/bin/
INSTALL_DIR = $(USRBIN)$(DIRNAME)

# Print all targets & their aim
default:
	$(ECHO) \"install\" script to $(INSTALL_DIR)
	$(ECHO) \"dist_clean\" removes all installed files
	$(ECHO) \"compress\" creates an archive $(ARCHIVE)
	$(ECHO) \"clean\" removes all non-required directories
	$(ECHO) \"release\" create release tar.gz
	$(ECHO) \"update\" update ./dep directory from submodule linkurios

update:
	cp $(LINKURIOUS)$(FILES) $(DEPENDENCY)

# Install the script to the specified dir and set the permission
install:
	@if [ -d $(INSTALL_DIR) ]; then printf "" ;else $(MKDIR) $(INSTALL_DIR); fi
	$(COPY) $(DEPENDENCY) $(INSTALL_DIR)
	$(COPY) $(SCRIPT) $(INSTALL_DIR)
	$(CHMOD) -R -x $(INSTALL_DIR)$(DEPENDENCY)*
	$(CHMOD) +x $(INSTALL_DIR)$(DEPENDENCY)
	$(LINK) $(INSTALL_DIR)$(SCRIPT) $(USRBIN)$(SCRIPT)
	$(CHMOD) +x $(USRBIN)$(SCRIPT)

# Remove all installed files & links
dist_clean:
	$(REMOVE) $(USRBIN)$(SCRIPT)
	$(REMOVE) $(INSTALL_DIR)

# Create a minimal archive for the cloud
compress:
	@if [ -d $(EXPORT) ]; then printf "" ;else $(MKDIR) $(EXPORT) ; fi
	$(TAR) $(EXPORT)$(NAME)$(ARCHIVE) $(DEPENDENCY) $(SCRIPT) Makefile

# Create a release
release:
	@if [ -d $(RELEASE)$(REL_NAME)$(INSTALL_DIR)/$(DEPENDENCY) ]; then printf "" ;else $(MKDIR) $(RELEASE)$(REL_NAME)$(INSTALL_DIR)/$(DEPENDENCY) ; fi
	@if [ -d $(RELEASE)$(REL_NAME)/DEBIAN ]; then printf "" ;else $(MKDIR) $(RELEASE)$(REL_NAME)/DEBIAN ; fi
	@if [ -d $(ARCH) ]; then printf "" ;else $(MKDIR) $(ARCH) ; fi
	find $(RELEASE) -maxdepth 1 -name "*.deb" -type f -exec mv -f {} $(ARCH) \;
	$(COPY) $(DEPENDENCY) $(RELEASE)$(REL_NAME)$(INSTALL_DIR)
	$(COPY) $(SCRIPT) $(RELEASE)$(REL_NAME)$(INSTALL_DIR)
	$(LINK) -r $(RELEASE)$(REL_NAME)$(INSTALL_DIR)$(SCRIPT) $(RELEASE)$(REL_NAME)$(USRBIN)$(SCRIPT)
	$(ECHO) Package: $(NAME) > $(CFG)
	$(ECHO) Version: $(MAJOR).$(GIT_REV) >> $(CFG)
	$(ECHO) Section: base >> $(CFG)
	$(ECHO) Priority: optional >> $(CFG)
	$(ECHO) Architecture: all >> $(CFG)
	$(ECHO) Depends: python \(\>= 2.7\) >> $(CFG)
	$(ECHO) Maintainer: $(DEV) $(EMAIL) >> $(CFG)
	$(ECHO) Homepage: https://github.com/fgerstmayer/dot2json >> $(CFG)
	$(ECHO) Description: $(REL_NAME) >> $(CFG)
	
	cd release && $(CHMOD) -R 755 $(REL_NAME) && fakeroot dpkg-deb --build $(REL_NAME)
	$(REMOVE) $(RELEASE)$(REL_NAME)
# Remove non required directories
clean:
	$(REMOVE) $(EXPORT)
	$(REMOVE) $(OTHER)
	

