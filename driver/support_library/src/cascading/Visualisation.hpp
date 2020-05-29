//
// Copyright © 2018-2020 Arm Limited. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include "../../include/ethosn_support_library/Support.hpp"

#include <ethosn_command_stream/CommandData.hpp>

#include <string>

namespace ethosn
{
namespace support_library
{

class Graph;
class OpGraph;
class GraphOfParts;
class Part;
struct Combination;
enum class Location;
enum class Lifetime;
enum class CompilerDataFormat;
enum class TraversalOrder;

std::string ToString(Location l);
std::string ToString(Lifetime l);
std::string ToString(CompilerDataFormat f);
std::string ToString(const TensorShape& s);
std::string ToString(TraversalOrder o);
std::string ToString(command_stream::MceOperation o);
std::string ToString(command_stream::PleOperation o);
std::string ToString(command_stream::BlockConfig b);

template <typename C>
std::string ArrayToString(const C& container)
{
    std::stringstream ss;
    ss << "[";
    for (auto it = container.begin(); it != container.end(); ++it)
    {
        ss << ToString(*it);
        if (it != (container.end() - 1))
        {
            ss << ", ";
        }
    }
    ss << "]";
    return ss.str();
}

struct DotAttributes
{
    DotAttributes() = default;
    DotAttributes(std::string id, std::string label, std::string color);

    std::string m_Id;
    std::string m_Label;
    std::string m_Shape;
    std::string m_Color;
};

enum class DetailLevel
{
    Low,
    High
};

/// Saves a graph of Ops and Buffers to a dot file format to visualise the graph.
/// detailLevel controls how much detail is shown on the visualisation.
void SaveOpGraphToDot(const OpGraph& graph, std::ostream& stream, DetailLevel detailLevel);

/// Saves a Graph of Nodes to a dot file format to visualise the graph.
/// Optionally includes groupings of Nodes into Parts, if provided a GraphOfParts object.
/// detailLevel controls how much detail is shown on the visualisation.
void SaveGraphToDot(const Graph& graph,
                    const GraphOfParts* graphOfParts,
                    std::ostream& stream,
                    DetailLevel detailLevel);

/// Saves all the plans generated for the given part to a dot file format to visualise them.
/// detailLevel controls how much detail is shown on the visualisation.
void SavePlansToDot(const Part& part, std::ostream& stream, DetailLevel detailLevel);

/// Saves a Combination of Plans and Glues to a dot file format to visualise it.
/// detailLevel controls how much detail is shown on the visualisation.
void SaveCombinationToDot(const Combination& combination,
                          const GraphOfParts& graphOfParts,
                          std::ostream& stream,
                          DetailLevel detailLevel);

}    // namespace support_library
}    // namespace ethosn
