const Event = artifacts.require("Event");

module.exports = function (deployer) {
  deployer.deploy(Event, 'no1', ['a','b','c'], 1711435654);
};
