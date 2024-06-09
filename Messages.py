def getCurrentPriceDetailedMessage(
    symbol: str,
    indicator: str,
    shortName: str,
    current_price: str,
    sign: str,
    diff: str,
    change_percentage: str,
):
    return f"""
Symbol:\t\t{symbol}\t\t{indicator}
Name:\t\t{shortName}
Current Price:\t\t₹{current_price}
Change:\t\t{sign} ₹{diff}\t\t(\t{sign}{change_percentage}%\t)\n\n
"""

def getCommandHelperMessage(starterMessage: str = ""):
    return (
        starterMessage
        + """
            
You can add a stock for monitoring by using `Add` command:
\t\t\tAdd MRPL
                 
Similary you can remove it by saying:
\t\t\tRemove MRPL

To see the existing list:
\t\t\t/showlist
                
To see the current movement of the stocks, use:
\t\t\t/current

you can see this message again by using:
\t\t\t/help
"""
    )
