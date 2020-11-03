Pramga solidity ^0.7.0;

contract Survey{

	uint votecounter; // how many times people have voted

	constructor() public{
		changecounter = 0;
	}

	function getdatabasechangenumber () public view returns(unit){
		return changecounter;
	}

	function incrementchangecounter() internal {
		changecounter = changecounter ++;
	}
}
