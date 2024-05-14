// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.6.0 <0.9.0;


contract Event {
 address public manager;
 string public eventName;
 uint public dueDate;
 bool public isAlive;
 Option[] public options;
 Player[] public players;
 Option public resultOption;

   struct Option {
      uint id;
      string name;
      uint256 count;
   }
   
   struct Player {
       address account;
       uint256 price;
       uint selection;
   }

   constructor(string memory name, string[] memory optionNames, uint due) {
       manager = msg.sender;
       eventName = name;
       dueDate = due;
       isAlive = true;
       for (uint i = 0 ; i < optionNames.length; i++) {
          options.push(Option({
            id: i,
            name: optionNames[i],
            count: 0
          }));
       }
   }

   function enter(uint selection) public payable {
       require(msg.sender != manager);
       require(msg.value > 0.01 ether);
      //  DEMO 先註解掉
      //  require(dueDate > block.timestamp);
       require(isAlive);
       Player memory player = Player({
        account: msg.sender,
        price: msg.value,
        selection: selection
       });
       players.push(player);

       for (uint i = 0 ; i < options.length ; i++) {
          if (options[i].id == selection) {
            options[i].count++;
          }
       }
   }

   function getProfile() public view returns (string memory, uint, Option[] memory, Player[] memory, bool, Option memory) {
       return (eventName, dueDate, options, players, isAlive, resultOption);
   }

   function getWinnerCount(uint selection) public view returns (uint256) {
      //統計贏家
      uint256 winnerCount = 0;
      for (uint i = 0 ; i < players.length ; i++) {
        if (players[i].selection == selection) {
            winnerCount++;
        }
      }
      return winnerCount;
   }

   function getTotalPrice() public view returns (uint256) {
      //取得總獎金額
      uint256 total = 0;
      for (uint i = 0 ; i < players.length ; i++) {
        total = total + players[i].price;
      } 
      return total;
   }

    function endEvent(uint selection) public {
        require(msg.sender == manager);
        require(isAlive);
        uint256 winnerCount = getWinnerCount(selection);
        uint256 total = getTotalPrice();
        
        for (uint i = 0 ; i < options.length ; i++) {
          if (options[i].id == selection) {
            resultOption = options[i];
            break;
          }
        }

        if (winnerCount == 0) {
          cancel();
        } else {
          isAlive = false;
          //手續費 5%
          uint256 fee = total / 20;

          payable(manager).transfer(fee);

          uint256 reward = (total-fee) / winnerCount;
          for (uint i = 0 ; i < players.length ; i++) {
            if (players[i].selection == selection) {
                payable(players[i].account).transfer(reward);
            }
          }
        }
        
   }
   
    function cancel() public {
      require(msg.sender == manager);
      require(isAlive);
      isAlive = false;
      for (uint i = 0 ; i < players.length ; i++) {
        payable(players[i].account).transfer(players[i].price);
      }
    }
}