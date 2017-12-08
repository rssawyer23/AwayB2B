x = seq(0,1,length=1000)
a = 695  # The number of wins observed
b = 675  # The number of losses observed
hx = dbeta(x,shape1=a,shape2=b)
plot(x, hx, type='l',lwd=2,xlab="Theta",ylab="Theta Posterior Density",xlim=c(0.25,0.75),ylim=c(0,35))
abline(v=0.5,col=3)
abline(v=0.528,col=2)
abline(v=0.7, col=2)
prob_greater_5 = 1 - pbeta(0.5, shape1=a, shape2=b);prob_greater_5
prob_greater_528 = 1 - pbeta(0.528, shape1=a, shape2=b);prob_greater_528
prob_greater_7 = 1 - pbeta(0.7, shape1=a, shape2=b);prob_greater_7
