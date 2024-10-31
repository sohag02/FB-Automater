# Capture new requests related to loading members
            # for request in driver.requests:
            #     if request.response:
            #         # Filter by URL if you know the specific endpoint for loading members
            #         if "graphql" in request.url:
            #             dctx = zstd.ZstdDecompressor()
            #             res = request.response.body.decode('utf-8', errors='ignore')
            #             decompressed_data = dctx.decompress(request.response.body)
            #             decoded_body = decompressed_data.decode('utf-8')  # Decode as UTF-8
            #             print("Decoded Response Body:")
            #             print(decoded_body)  # Check the decoded response
                        

                        # content_type = request.response.headers.get('Content-Type', '')
                        # print(content_type)
                        # with open('members.json', 'w') as f:
                        #     f.write(res)
                        # print("Wrote")
                        # print(res, "res")
                        # print(request.response)
                        
                        # print(True if request.body else False)
                        # json_res = json.loads(decoded_body)
                        # with open('members.json', 'w') as f:
                        #     json.dump(json_res, f, indent=4)
                        # members = json_res['data']['node']['new_members']['edges']
                        # for member in members:
                        #     process_member(member)