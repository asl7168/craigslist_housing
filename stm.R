require("stm")
#require("sjPlot")
#require("igraph")
data <- read.csv("./csv_dumps/all_complete.csv")

#clean text
processed <- textProcessor(data$documents, metadata = data)

#test different lower.thresh values
#plotRemoved(processed$documents, lower.thresh = seq(1, 50, by = 25))

#prepare texts for stm
out <- prepDocuments(processed$documents, processed$vocab, processed$meta,lower.thresh = 20)
meta <- out$meta

#primary stm model
prevFit <- stm(documents = out$documents, vocab = out$vocab, K = 7, prevalence =~ race * poverty, max.em.its = 200, data = meta, init.type = "Spectral")

#get top associations with topics
labelTopics(prevFit)

#see associations between topics and metadata
prep <- estimateEffect(1:7 ~ race * poverty, prevFit, meta = meta, uncertainty = "Global")
summary(prep)

#see top words
plot(prevFit,type="labels")

#get examples for certain topics
z<- data$documents[-processed$docs.removed]
#y<-z[-out$docs.removed]
thoughts1 <- findThoughts(prevFit,texts = z, n=2, topics = 1)$docs[[1]]
#par(mfrow = c(1,2),mar = c(0.5,0.5,1,0.5))
plotQuote(thoughts1, width = 30, main = "Topic 1")

#different model to see how certain words are more common with certain groups within a single topic
contentFit <- stm(documents = out$documents, vocab = out$vocab, K = 7, prevalence =~ is_white * poverty, content =~ is_white, max.em.its = 200, data = meta, init.type = "Spectral")
plot(contentFit, type = "perspectives",topics = 1)
labelTopics(contentFit)

prep2 <- estimateEffect(1:7 ~ race * poverty, contentFit, meta = meta, uncertainty = "Global")
summary(prep2)

plot(contentFit,type="labels")

