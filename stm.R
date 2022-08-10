require("stm")
#require("sjPlot")
#require("igraph")
data <- read.csv("./csv_dumps/all_complete.csv")
processed <- textProcessor(data$documents, metadata = data)
#plotRemoved(processed$documents, lower.thresh = seq(1, 50, by = 25))
out <- prepDocuments(processed$documents, processed$vocab, processed$meta,lower.thresh = 20)
meta <- out$meta
#contrasts(meta$class) = contr.sum(8)
prevFit <- stm(documents = out$documents, vocab = out$vocab, K = 7, prevalence =~ race * poverty, max.em.its = 200, data = meta, init.type = "Spectral")


contentFit <- stm(documents = out$documents, vocab = out$vocab, K = 7, prevalence =~ is_white * poverty, content =~ is_white, max.em.its = 200, data = meta, init.type = "Spectral")
plot(contentFit, type = "perspectives",topics = 1)

z<- data$documents[-processed$docs.removed]
y<-z[-out$docs.removed]
thoughts1 <- findThoughts(prevFit,texts = y, n=2, topics = 1)$docs[[1]]
par(mfrow = c(1,2),mar = c(0.5,0.5,1,0.5))
plotQuote(thoughts1, width = 30, main = "Topic 1")


labelTopics(prevFit)
prep <- estimateEffect(1:7 ~ race * poverty, prevFit, meta = meta, uncertainty = "Global")
summary(prep)
#plot_model(prevFit, type='int')
#mod.out.corr <- topicCorr(prevFit)
plot(prevFit,type="labels")