from vectorSearch import VectorSearch


vs = VectorSearch()


#single file
#vs.store("files/obligatory_assignment.pdf")

#folder
print(vs.store_folder("files/slides"))