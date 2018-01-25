CC := g++
CFLAGS := -Wall -g
#LFLAGS := -Wl,--verbose
NAME := mzk_oggcover

#src is needed because -I"" fails
P_INCLUDES := -I"."
P_LINKS := -L"/usr/local/lib"
LINKS :=

FILE_EXT := .cpp
CDIR := .
OBJDIR := obj

CPP_FILES := $(shell find $(CDIR)/ -type f -name "*$(FILE_EXT)")
OBJ_FILES := $(foreach cppfile,$(CPP_FILES:$(FILE_EXT)=.o), $(subst $(CDIR)/,$(OBJDIR)/,$(cppfile)))
DEPENDENCIES = $(OBJ_FILES:.o=.d)

$(NAME): $(OBJ_FILES)
	@echo Linking object files for $(NAME)
	@$(CC) $(LFLAGS) $(P_LINKS) $^ -o $@ $(LINKS)

$(OBJDIR)/%.o: $(CDIR)/%$(FILE_EXT)
	@mkdir -p $(@D)
	@echo Compiling $<
	@$(CC) $(CFLAGS) $(P_INCLUDES) -c $< -o $@

.PHONY: reset
reset :
	@echo Wiping object files
	@rm -r $(OBJDIR)
	@echo Rebuilding $(NAME) from scratch
	@make

-include $(DEPENDENCIES)
