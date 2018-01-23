#include <iostream>
#include <string>

#include "base64.h"

#define RETURN_OK 0
#define ERR_ARGS  1
#define ERR_MIME  2

unsigned int read_int_from_char_it(std::vector<unsigned char>::iterator &it)
{
	unsigned int r = *(it) << 24 | *(it + 1) << 16 | *(it + 2) << 8 | *(it + 3);
	it += 4;
	return r;

}

int main(int argc, char **argv)
{
	//Get the data from stdin
	std::string input;
	std::cin >> input;

	//decode the base64
	std::vector<unsigned char> data = base64_decode(input);
	std::vector<unsigned char>::iterator it = data.begin();

	//cf flac METADATA_BLOCK_PICTURE spec
	read_int_from_char_it(it);

	//Read the MIME type
	unsigned int mime_len  = read_int_from_char_it(it);
	std::string  mime_type(it, it + mime_len);
	it += mime_len;

	if(mime_type != "image/jpeg" && mime_type != "image/jpg" && mime_type != "image/png")
	{
		std::cout << "Unsupported image type " << mime_type << std::endl << "Only image/jpeg and image/png are supported" << std::endl;
		return ERR_MIME;
	}

	//Skip description
	it += read_int_from_char_it(it);
	//Skip image size, colour format, and file size
	it += 5 * sizeof(unsigned int);

	std::cout << std::string(it, data.end());

	return RETURN_OK;
}
