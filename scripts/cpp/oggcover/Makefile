CC := g++
CFLAGS := -Wall -g
#LFLAGS := -Wl,--verbose

#src is needed because -I"" fails
P_INCLUDES := -I"."
P_LINKS := -L"/usr/local/lib"
LINKS :=

FILE_EXT := .cpp
SRCDIR   := .
OBJDIR   := obj
OUTDIR   := ../../bin
NAME     := oggcover

CPP_FILES := $(shell find $(SRCDIR)/ -type f -name "*$(FILE_EXT)")
OBJ_FILES := $(foreach cppfile,$(CPP_FILES:$(FILE_EXT)=.o), $(subst $(SRCDIR)/,$(OBJDIR)/,$(cppfile)))
DEPENDENCIES = $(OBJ_FILES:.o=.d)

$(OUTDIR)/$(NAME): $(OBJ_FILES)
	@mkdir -p $(@D)
	@echo Linking object files for $(NAME)
	@$(CC) $(LFLAGS) $(P_LINKS) $^ -o $@ $(LINKS)

$(OBJDIR)/%.o: $(SRCDIR)/%$(FILE_EXT)
	@mkdir -p $(@D)
	@echo Compiling $<
	@$(CC) $(CFLAGS) $(P_INCLUDES) -c $< -o $@

.PHONY: reset
reset :
	@if [ -d "$(OBJDIR)" ]; then echo Wiping object files; rm -r $(OBJDIR); fi
	@echo Rebuilding $(NAME) from scratch
	@make

-include $(DEPENDENCIES)
